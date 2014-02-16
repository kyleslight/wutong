-- host     : localhost
-- database : postgresql
-- port     : 5432
-- encoding : utf-8

--------------------------------------------------------------------------------
-- function
--------------------------------------------------------------------------------
-- `account` is `nickname` or `email`
create or replace function
get_uid(_account text) returns int
as $$
  select uid
    from myuser
   where nickname = _account
      or email = _account;
$$ language sql;

create or replace function
do_user_register(_nickname text, _password text, _email email) returns int
as $$
declare
  _uid int;
  _tmp text;
begin
  _tmp := null;

  select uid from myuser where nickname = _nickname into _uid;
  if _uid is not null then
    _tmp := -1;
  else
    select uid from myuser where email = _email into _uid;
    if _uid is not null then
      _tmp := -2;
    end if;
  end if;

  if _uid is null then
    insert into myuser
        (nickname, password, email)
    values
        (_nickname, crypt(_password, gen_salt('bf')), _email)
    returning uid into _tmp;
  end if;

  return _tmp;
end;
$$ language plpgsql;

create or replace function
do_user_activate(_uid int) returns int
as $$
  update myuser
     set is_activated = true
   where uid = _uid
  returning uid;
$$ language sql;

create or replace function
do_user_login(_account text, _password text) returns json
as $$
  select row_to_json(j.*)
    from
      (
         select *
           from myuser
          where _account = any(array[nickname, email])
            and password = crypt(_password, password)
      ) j;
$$ language sql;

create or replace function
get_user(_uid int) returns json
as $$
  select row_to_json(j.*)
    from
      (
         select *
           from myuser
          where uid = _uid
      ) j;
$$ language sql;

create or replace function
create_user_collection(_uid int, _type sort, _relevant_id int) returns void
as $$
  insert into user_collection
      (uid, type, relevant_id)
  values
      (_uid, _type, _relevant_id);
$$ language sql;

create or replace function
get_user_collections(_uid int, _type sort, _limit int, _offset int) returns json
as $$
declare
  _idname text;
  _tabname text;
  _tmp json;
begin
  if _type = '1' then
    _tabname := 'article_base';
    _idname := 'aid';
  elseif _type = '2' then
    _tabname := 'group_topic';
    _idname := 'tid';
  end if;

  execute '
  select array_to_json(array_agg(aj))
    from
      (
         select *
           from ' || _tabname::regclass || '
          where ' || quote_ident(_idname) || ' in (select relevant_id
                         from user_collection
                        where uid = ' || _uid || '
                          and type = ' || quote_literal(_type) || '
                        order by id
                        limit ' || _limit || '
                       offset ' || _offset || ')
      ) aj'
    into _tmp;
  return _tmp;
end;
$$ language plpgsql;

create or replace function
get_user_msgs(_uid int, _type sort, _limit int, _offset int) returns json
as $$
  select array_to_json(array_agg(aj))
    from
      (
         select *
           from user_message
          where uid = _uid
            and type = _type
          order by id
          limit _limit
         offset _offset
      ) aj;
$$ language sql;

-- 用户的未读消息的统计信息
create or replace function
get_user_unread_msg_count(_uid int) returns json
as $$
  select array_to_json(array_agg(aj))
    from
      (
         select type,
                count(id) as "sum"
           from user_message
          where uid = _uid
            and not is_viewed
          group by type
      ) aj;
$$ language sql;

create or replace function
get_user_article_list(_uid int, _limit int, _offset int) returns json
as $$
  select array_to_json(array_agg(aj.*))
    from
      (
        select i.*,
               a.create_time,
               a.title
          from article_interact_info i,
               article a
         where a.uid = _uid
           and i.aid = a.aid
         order by a.aid desc
         limit _limit
        offset _offset
      ) aj;
$$ language sql;

create or replace function
get_user_stars(_uid int, _limit int, _offset int) returns json
as $$
  select array_to_json(array_agg(aj.*))
    from
      (
        select u.*
          from user_relationship r,
               user_base u
         where r.uid = u.uid
           and r.uid = _uid
           and r.relate_level = '2'
         order by r.id desc
         limit _limit
        offset _offset
      ) aj;
$$ language sql;

create or replace function
get_user_followers(_uid int, _limit int, _offset int) returns json
as $$
  select array_to_json(array_agg(aj.*))
    from
      (
        select u.*
          from user_relationship r,
               user_base u
         where r.uid = u.uid
           and r.another_uid = _uid
           and r.relate_level = '2'
         order by r.id desc
         limit _limit
        offset _offset
      ) aj;
$$ language sql;

create or replace function
get_user_viewed_articles(_uid int, _limit int, _offset int) returns json
as $$
  select array_to_json(array_agg(aj.*))
    from
      (
        select a.*,
               v.time as "view_time"
          from article_base a,
               article_view v
         where v.aid = a.aid
           and v.uid = _uid
         order by v.id desc
         limit _limit
        offset _offset
      ) aj;
$$ language sql;

create or replace function
get_user_homepage(_nickname text) returns json
as $$
declare
  _uid int;
  _tmp json;
begin
  select uid
    from myuser
   where nickname = _nickname
    into _uid;

  select row_to_json(j.*)
    from
      (
         select *,
                0 as "score",
                (select name from user_honor where uid = _uid) as "user_titles",
                (select count(id) from user_relationship where relate_level = '2' and uid = _uid) as "star_num",
                (select count(id) from user_relationship where relate_level = '2' and another_uid = _uid) as "follower_num",
                (select get_user_stars(_uid, 8, 0)) as "stars",
                (select get_user_followers(_uid, 8, 0)) as "followers",
                (select get_user_article_list(_uid, 10, 0)) as "articles",
                (select get_user_viewed_articles(_uid, 10, 0)) as "viewed_articles"
           from user_show
          where nickname = _nickname
      ) j
    into _tmp;

  return _tmp;
end;
$$ language plpgsql;

create or replace function
create_user_memo(_uid int, _title text, _content text) returns json
as $$
declare
  _tmp user_memo;
  _res json;
begin
  insert into user_memo
      (uid, title, content)
  values
      (_uid, _title, _content)
  returning * into _tmp;

  select row_to_json(_tmp.*) into _res;
  return _res;
end;
$$ language plpgsql;

create or replace function
get_user_memo(_uid int, _id int) returns json
as $$
  select row_to_json(j.*)
    from
      (
         select *
           from user_memo
          where id = _id
            and uid = _uid
      ) j;
$$ language sql;

create or replace function
get_user_memos(_uid int, _limit int, _offset int) returns json
as $$
  select array_to_json(array_agg(aj))
    from
      (
         select id,
                title,
                content,
                create_time
           from user_memo
          where uid = _uid
          order by id desc
          limit _limit
         offset _offset
      ) aj;
$$ language sql;

create or replace function
update_user_memo(_uid int, _id int, _title text, _content text) returns json
as $$
declare
  _tmp user_memo;
  _res json;
begin
  update user_memo
     set title = _title,
         content = _content
   where uid = _uid
     and id = _id
  returning * into _tmp;

  select row_to_json(_tmp.*) into _res;
  return _res;
end;
$$ language plpgsql;


create or replace function
create_article(
    _uid int,
    _title text,
    _mainbody text,
    _intro text,
    _suit_for text,
    _refers text[],
    _series text,
    _resources text[],
    _public_level sort) returns int
as $$
  insert into article
      (uid, title, mainbody, intro, suit_for, refers, series, resources, public_level)
  values
      (_uid, _title, _mainbody, _intro, _suit_for, _refers, _series, _resources, _public_level)
  returning aid;
$$ language sql;

create or replace function
update_article_tags(_aid int, _tags text[]) returns void
as $$
declare
  _tag text;
begin
  PERFORM id
     from article_tag
    where aid = _aid;
  if FOUND then
    delete from article_tag where aid = _aid;
  end if;
  foreach _tag in array _tags
  loop
    insert into article_tag (aid, content) values (_aid, _tag);
  end loop;
end;
$$ language plpgsql;

create or replace function
update_article_coeditors(_aid int, _nicknames text[]) returns void
as $$
declare
  _nickname text;
begin
  perform id
     from article_coeditor
    where aid = _aid;
  if FOUND then
    delete from article_coeditor where aid = _aid;
  end if;
  foreach _nickname in array _nicknames
  loop
    insert into article_coeditor (aid, nickname) values (_aid, _nickname);
  end loop;
end;
$$ language plpgsql;

create or replace function
get_article(_aid int) returns json
as $$
  select row_to_json(j.*)
    from
      (
         select *
           from article_show
          where aid = _aid
      ) j;
$$ language sql;

create or replace function
get_articles(_limit int, _offset int, _tag text) returns json
as $$
  select array_to_json(array_agg(aj.*))
    from
      (
          select *
            from article_base
           where not is_deleted
             and public_level > '2'
             and (_tag is null or _tag = any(tags))
           order by modify_time desc
           limit _limit
          offset _offset
      ) aj;
$$ language sql;

create or replace function
get_bottom_comments(_aid int, _limit int, _offset int) returns json
as $$
  select array_to_json(array_agg(aj.*))
    from
      (
          select *
            from article_bottom_comment_show
           where aid = _aid
           order by rank desc
           limit _limit
          offset _offset
      ) aj;
$$ language sql;

create or replace function
get_side_comments(_aid int) returns json
as $$
  select array_to_json(array_agg(aj.*))
    from
      (
          select *
            from article_side_comment_show
           where aid = _aid
      ) aj;
$$ language sql;

create or replace function
get_bottom_comment(_id int) returns json
as $$
  select row_to_json(j.*)
    from
      (
          select *
            from article_bottom_comment_show
           where id = _id
      ) j;
$$ language sql;

create or replace function
get_side_comment(_id int) returns json
as $$
  select row_to_json(j.*)
    from
      (
          select *
            from article_side_comment_show
           where id = _id
      ) j;
$$ language sql;

create or replace function
create_bottom_comment(
    _aid int,
    _uid int,
    _content text,
    _reply_id int) returns json
as $$
declare
  _tmp int;
begin
  select max(rank) + 1
    from article_bottom_comment
   where aid = _aid
    into _tmp;
  if _tmp is null then
      _tmp := 1;
  end if;

  insert into article_bottom_comment
      (aid, uid, reply_id, content, rank)
  values
      (_aid, _uid, _reply_id, _content, _tmp)
  returning id into _tmp;
  return get_bottom_comment(_tmp);
end;
$$ language plpgsql;

create or replace function
create_side_comment(
    _aid int,
    _uid int,
    _content text,
    _paragraph_id text) returns json
as $$
declare
  _tmp int;
begin
  insert into article_side_comment
      (aid, uid, content, paragraph_id)
  values
      (_aid, _uid, _content, _paragraph_id)
  returning id into _tmp;
  return get_side_comment(_tmp);
end;
$$ language plpgsql;

create or replace function
create_article_view(_aid int, _uid int, _ip inet) returns void
as $$
declare
    _tmp int;
begin
  perform id
     from article_view
    where aid = _aid
      and (uid = _uid or ip = _ip);
  if FOUND then
    if _uid > 0 then
      update article_view
         set ip = _ip,
             time = now()
       where aid = _aid
         and uid = _uid;
    end if;
  else
    insert into article_view
        (aid, uid, ip)
    values
        (_aid, _uid, _ip);
  end if;
end;
$$ language plpgsql;

create or replace function
get_article_interaction(_aid int) returns json
as $$
  select row_to_json(j.*)
    from
      (
          select *
            from article_interact_info
           where aid = _aid
      ) j;
$$ language sql;

create or replace function
get_myinteraction_info(_aid int, _uid int) returns json
as $$
declare
    _score int;
    _is_viewed bool;
    _is_collected bool;
    _is_forwarded bool;
    _tmp json;
begin
  select score
    from article_score
   where aid = _aid
     and uid = _uid
    into _score;

  perform id
     from article_view
    where aid = _aid
      and uid = _uid;
  if FOUND then
    _is_viewed := true;
  else
    _is_viewed := false;
  end if;

  perform id
     from article_collection
    where aid = _aid
      and uid = _uid;
  if FOUND then
    _is_collected := true;
  else
    _is_collected := false;
  end if;

  perform id
     from article_forwarded
    where aid = _aid
      and uid = _uid;
  if FOUND then
    _is_forwarded := true;
  else
    _is_forwarded := false;
  end if;

  select row_to_json(j.*)
    from
      (
         select _score as "score",
                _is_viewed as "is_viewed",
                _is_collected as "is_collected",
                _is_forwarded as "is_forwarded"
      ) j
    into _tmp;
  return _tmp;
end;
$$ language plpgsql;

create or replace function
update_myinteraction_info(_aid int, _uid int, _value text, _tabname text) returns int
as $$
declare
    _tmp int;
begin
  execute 'delete from '
      || _tabname::regclass
      || ' where aid = ' || _aid
      || '   and uid = ' || _uid;
  get diagnostics _tmp = ROW_COUNT;
  if _tabname = 'article_score' then
    insert into article_score
        (aid, uid, score)
    values
        (_aid, _uid, _value);
  elseif _tmp = 0 then
    execute format('insert into %I (aid, uid) values (%s, %s)', _tabname, _aid, _uid);
  end if;
  return _tmp;
end;
$$ language plpgsql;


create or replace function
get_group_homepage(_gid int) returns json
as $$
declare
    _tmp json;
begin
  return _tmp;
end;
$$ language plpgsql;
-- create or replace function
-- get_group_sessions(_gid int)
--   returns json
-- as $$
--     select array_to_json(array_agg(aj))
--       from
--         (
--             select *
--               from
--                 (
--                     select row_to_json(j.*)::text, j.reply_time
--                       from
--                         (
--                             select *
--                               from group_topic
--                              where gid = _gid
--                         ) j
--                     union
--                     select row_to_json(j.*)::text, j.reply_time
--                       from
--                         (
--                             select *
--                               from group_message
--                              where gid = _gid
--                         ) j
--                 ) s
--              order by s.reply_time
--         ) aj;
-- $$ language sql;


-- create or replace function
-- get_notifications(_uid int, _limit int, _offset int)
--   returns json
-- as $$
--     select array_to_json(array_agg(aj))
--       from
--         (
--             select *
--               from notification
--              where uid = _uid
--              limit _limit
--             offset _offset
--         ) aj;
-- $$ language sql;


-- create or replace function
-- create_notification(
--     _uid int,
--     _nickname varchar,
--     _title varchar,
--     _content varchar,
--     _type varchar,
--     _url varchar)
--   returns int
-- as $$
-- declare
--     _tmp int;
-- begin
--     insert into notification
--         (uid, receiver, title, content, type, url)
--     values
--         (_uid, _nickname, _title, _content, _type, _url)
--     returning id into _tmp;
--     return _tmp;
-- end;
-- $$ language plpgsql;


-- create or replace function
-- get_user_groups(_uid int, _limit int, _offset int)
--   returns json
-- as $$
--     select array_to_json(array_agg(aj))
--       from
--         (
--             select g.gid, g.name
--               from group_user gu,
--                    "group" g
--              where gu.uid = _uid
--                and gu.gid = g.gid
--              limit _limit
--             offset _offset
--         ) aj;
-- $$ language sql;


-- create or replace function
-- get_group_permission(_gid int, _uid int)
--   returns json
-- as $$
--     select row_to_json(j.*)
--       from
--         (
--             select *
--               from group_user
--              where gid = _gid
--                and uid = _uid
--         ) j;
-- $$ language sql;


-- create or replace function
-- get_group_info(_gid int)
--   returns json
-- as $$
--     select row_to_json(j.*)
--       from
--         (
--             select *
--               from group_info_v
--              where gid = _gid
--         ) j;
-- $$ language sql;


-- create or replace function
-- create_group(
--     _uid int,
--     _name varchar,
--     _intro varchar,
--     _motto varchar,
--     _avatar varchar,
--     _banner varchar,
--     _is_public bool)
--   returns int
-- as $$
--     insert into "group"
--         (uid, name, intro, motto, avatar, banner, is_public)
--     values
--         (_uid, _name, _intro, _motto, _avatar, _banner, _is_public)
--     returning gid;
-- $$ language sql;


-- create or replace function
-- join_group(_gid int, _uid int)
--   returns int
-- as $$
--     insert into group_user
--         (gid, uid)
--     select _gid, _uid
--      where not exists
--         (
--             select guid
--               from group_user
--              where gid = _gid
--                and uid = _uid
--         )
--     returning guid;
-- $$ language sql;


-- create or replace function
-- get_group_tags(_gid int)
--   returns json
-- as $$
--     select array_to_json(array_agg(aj))
--       from
--         (
--             select name
--               from group_tag
--              where gid = _gid
--         ) aj;
-- $$ language sql;


-- create or replace function
-- get_group_member_info(_gid int, _uid int)
--   returns json
-- as $$
--     select row_to_json(j.*)
--       from
--         (
--             select *
--               from group_member_info_v
--              where gid = _gid
--                and uid = _uid
--         ) j;
-- $$ language sql;


-- create or replace function
-- get_group_members(_gid int, _limit int, _offset int)
--   returns json
-- as $$
--     select array_to_json(array_agg(aj))
--       from
--         (
--             select *
--               from group_member_info_v
--              where gid = _gid
--              order by guid desc
--              limit _limit
--             offset _offset
--         ) aj;
-- $$ language sql;


-- create or replace function
-- get_group_chats(_gid int, _limit int, _offset int)
--   returns json
-- as $$
--     select array_to_json(array_agg(aj))
--       from
--         (
--             select *
--               from group_chat_v
--              where gid = _gid
--              order by id desc
--              limit _limit
--             offset _offset
--         ) aj;
-- $$ language sql;


-- create or replace function
-- get_group_chat(_id int)
--   returns json
-- as $$
--     select row_to_json(j.*)
--       from
--         (
--             select *
--               from group_chat_v
--              where id = _id
--         ) j;
-- $$ language sql;


-- create or replace function
-- create_topic(
--     _gid int,
--     _uid int,
--     _title varchar,
--     _content varchar,
--     _reply_id int)
--   returns int
-- as $$
--     insert into topic
--         (gid, uid, title, content, reply_id)
--     values
--         (_gid, _uid, _title, _content, _reply_id)
--     returning tid;
-- $$ language sql;


-- create or replace function
-- get_topics(_limit int, _offset int)
--   returns json
-- as $$
--     select array_to_json(array_agg(aj))
--       from
--         (
--             select gt.*,
--                    g.name as "group_name"
--               from group_topic_v gt,
--                    "group" g
--              where gt.gid = g.gid
--              order by last_reply_time desc
--              limit _limit
--             offset _offset
--         ) aj;
-- $$ language sql;


-- create or replace function
-- get_topics_by_tag(_tag varchar, _limit int, _offset int)
--   returns json
-- as $$
--     select array_to_json(array_agg(aj))
--       from
--         (
--             select gt.*,
--                    g.name as "group_name"
--               from group_topic_v gt,
--                    "group" g,
--                    group_tag g_tag
--              where gt.gid = g.gid
--                and gt.gid = g_tag.gid
--                and g_tag.name = _tag
--              order by last_reply_time desc
--              limit _limit
--             offset _offset
--         ) aj;
-- $$ language sql;


-- create or replace function
-- get_group_topics(_gid int, _limit int, _offset int)
--   returns json
-- as $$
--     select array_to_json(array_agg(aj))
--       from
--         (
--             select *
--               from group_topic_v
--              where gid = _gid
--              order by tid desc
--              limit _limit
--             offset _offset
--         ) aj;
-- $$ language sql;


-- create or replace function
-- get_user_topics(_uid int, _limit int, _offset int)
--   returns json
-- as $$
--     select array_to_json(array_agg(aj))
--       from
--         (
--             select gt.*,
--                    g.name as "group_name"
--               from group_topic_v gt,
--                    "group" g,
--                    group_user gu
--              where gt.gid = g.gid
--                and gu.gid = g.gid
--                and gu.uid = _uid
--                and gu.is_member
--              order by last_reply_time desc
--              limit _limit
--             offset _offset
--         ) aj;
-- $$ language sql;


-- create or replace function
-- get_topic(_tid int)
--   returns json
-- as $$
--     select row_to_json(j.*)
--       from
--         (
--             select *
--               from group_topic_v
--              where tid = _tid
--         ) j;
-- $$ language sql;


-- create or replace function
-- get_topic_topics(_reply_id int, _limit int, _offset int)
--   returns json
-- as $$
--     select array_to_json(array_agg(aj))
--       from
--         (
--             select *
--               from group_topic_v
--              where reply_id = _reply_id
--              order by tid desc
--              limit _limit
--             offset _offset
--         ) aj;
-- $$ language sql;


-- create or replace function
-- get_topic_chats(_reply_id int, _limit int, _offset int)
--   returns json
-- as $$
--     select array_to_json(array_agg(aj))
--       from
--         (
--             select *
--               from group_chat_v
--              where reply_id = _reply_id
--              order by id desc
--              limit _limit
--             offset _offset
--         ) aj;
-- $$ language sql;


-- create or replace function
-- create_group_chat(
--     _gid int,
--     _uid int,
--     _content varchar,
--     _reply_id int)
--   returns int
-- as $$
--     insert into group_chat
--         (gid, uid, content, reply_id)
--     values
--         (_gid, _uid, _content, _reply_id)
--     returning id;
-- $$ language sql;


-- create or replace function
-- get_topic_messages(_tid int, _limit int, _offset int)
--   returns json
-- as $$
--     select array_to_json(array_agg(aj))
--       from
--         (
--             select *
--               from group_message_v
--              where reply_id = _tid
--              order by last_reply_time desc
--              limit _limit
--             offset _offset
--         ) aj;
-- $$ language sql;


-- create or replace function
-- get_group_message(_message_id int)
--   returns json
-- as $$
--     select row_to_json(j.*)
--       from
--         (
--             select *
--               from group_message_v
--              where id = _message_id
--         ) j;
-- $$ language sql;


-- create or replace function
-- get_group_messages(_gid int, _limit int, _offset int)
--   returns json
-- as $$
--     select array_to_json(array_agg(aj))
--       from
--         (
--             select *
--               from group_message_v
--              where gid = _gid
--                and reply_id is null
--              order by last_reply_time desc
--              limit _limit
--             offset _offset
--         ) aj;
-- $$ language sql;


-- create or replace function
-- get_topic_messages(_tid int, _limit int, _offset int)
--   returns json
-- as $$
--     select array_to_json(array_agg(aj))
--       from
--         (
--             select *
--               from group_message_v
--              where reply_id = _tid
--              order by last_reply_time desc
--              limit _limit
--             offset _offset
--         ) aj;
-- $$ language sql;


-- create or replace function
-- get_group_bulletins(_gid int, _limit int, _offset int)
--   returns json
-- as $$
--     select array_to_json(array_agg(aj))
--       from
--         (
--             select *
--               from group_bulletin_v
--              where gid = _gid
--              order by id desc
--              limit _limit
--             offset _offset
--         ) aj;
-- $$ language sql;


-- create or replace function
-- create_group_bulletin(
--     _gid int,
--     _uid int,
--     _title varchar,
--     _content varchar)
--   returns int
-- as $$
--     insert into group_bulletin
--         (gid, uid, title, content)
--     values
--         (_gid, _uid, _title, _content)
--     returning id;
-- $$ language sql;


-- create or replace function
-- is_article_author(_aid int, _uid int)
--   returns bool
-- as $$
-- declare
--     _res bool;
-- begin
--     select true
--       from article
--      where aid = _aid
--        and uid = _uid
--       into _res;
--     if _res is null then
--         _res := false;
--     end if;
--     return _res;
-- end;
-- $$ language plpgsql;



-- create or replace function
-- get_article_collections(_uid int, _limit int, _offset int)
--   returns json
-- as $$
--     select array_to_json(array_agg(aj.*))
--       from
--         (
--             select *,
--                    get_article_tags(a.aid) as "tags"
--               from article_collection_v a
--              where uid = _uid
--              order by id desc
--              limit _limit
--             offset _offset
--         ) aj;
-- $$ language sql;



-- create or replace function
-- create_article_view(_aid int, _uid int, _ip varchar)
--   returns int
-- as $$
--     insert into article_view
--         (aid, uid, ip)
--     select _aid, _uid, _ip
--      where not exists
--         (
--             select uid, ip
--               from article_view
--              where aid = _aid
--                and (uid = _uid or ip = _ip)
--         )
--     returning id;
-- $$ language sql;


-- create or replace function
-- create_article_collection(_aid int, _uid int)
--   returns int
-- as $$
--     insert into article_collection
--         (aid, uid)
--     select _aid, _uid
--      where not
--         (
--             select is_article_author(_aid, _uid)
--         )
--     returning id;
-- $$ language sql;


-- create or replace function
-- create_article_score(_aid int, _uid int, _score int)
--   returns int
-- as $$
--     insert into article_score
--         (aid, uid, score)
--     select _aid, _uid, _score
--      where not
--         (
--             select is_article_author(_aid, _uid)
--         )
--     returning id;
-- $$ language sql;


-- create or replace function
-- count_article_view(_aid int)
--   returns bigint
-- as $$
--     select count(aid)
--       from article_view
--      where aid = _aid
-- $$ language sql;


-- create or replace function
-- count_article_collection(_aid int)
--   returns bigint
-- as $$
--     select count(aid)
--       from article_collection
--      where aid = _aid
-- $$ language sql;


-- create or replace function
-- calc_article_score(_aid int)
--   returns numeric
-- as $$
--     select coalesce(avg(score), 0)
--       from article_score
--      where aid = _aid
-- $$ language sql;


-- create or replace function
-- get_article_info(_aid int)
--   returns json
-- as $$
--     select row_to_json(j.*)
--       from
--         (
--             select *,
--                    (select get_article_tags($1)) as "tags",
--                    (select count_article_view($1)) as "views",
--                    (select calc_article_score($1)) as "score",
--                    (select count_article_collection($1)) as "collections"
--               from article_info_v
--              where aid = _aid
--         ) j;
-- $$ language sql;



-- create or replace function
-- get_comment(_id int)
--   returns json
-- as $$
--     select row_to_json(j.*)
--       from
--         (
--             select *
--               from article_comment_v
--              where id = _id
--         ) j;
-- $$ language sql;


-- create or replace function
-- get_search_opus(_aid int)
--   returns json
-- as $$
--     select row_to_json(j.*)
--       from
--         (
--             select *,
--                    (select get_article_tags(id)) as "tags"
--               from search_article_v
--              where id = _aid
--         ) j;
-- $$ language sql;


-- create or replace function
-- get_search_group(_gid int)
--   returns json
-- as $$
--     select row_to_json(j.*)
--       from
--         (
--             select *,
--                    (select get_group_tags(id)) as "tags"
--               from search_group_v
--              where id = _gid
--         ) j;
-- $$ language sql;


-- create or replace function
-- get_search_user(_uid int)
--   returns json
-- as $$
--     select row_to_json(j.*)
--       from
--         (
--             select *
--               from search_user_v
--              where id = _uid
--         ) j;
-- $$ language sql;


-- create or replace function article_before_t() returns trigger
-- as $$
-- begin
--     if (tg_op = 'DELETE') then
--         delete from article_history where aid = old.aid;
--         delete from article_honor where aid = old.aid;
--         delete from article_appositeness where aid = old.aid;
--         delete from article_tag where aid = old.aid;
--         delete from article_comment where aid = old.aid;
--         delete from article_view where aid = old.aid;
--         delete from article_user where aid = old.aid;
--         return old;
--     elsif (tg_op = 'UPDATE') then
--         insert into article_history (
--             aid, title, mainbody,
--             description, reference, series, resource)
--         select aid, title,
--                mainbody,
--                description, reference,
--                series, resource
--           from article
--          where aid = old.aid;
--         return new;
--     end if;
--     return null;
-- end;
-- $$ language plpgsql;


-- create or replace function article_after_t() returns trigger
-- as $$
-- begin
--     if (tg_op = 'INSERT') then
--         update article set last_modify_time = submit_time where aid = new.aid;
--         return new;
--     end if;
--     return null;
-- end;
-- $$ language plpgsql;


-- create or replace function topic_before_t() returns trigger
-- as $$
-- begin
--     if (tg_op = 'DELETE') then
--         delete from group_chat where reply_id = old.tid;
--         delete from topic where reply_id = old.tid;
--         return old;
--     end if;
--     return null;
-- end;
-- $$ language plpgsql;


-- create or replace function topic_after_t() returns trigger
-- as $$
-- begin
--     if (tg_op = 'INSERT') then
--         update topic
--            set last_reply_time = now(),
--                reply_times = reply_times + 1
--          where tid = new.tid;
--         return new;
--     end if;
--     return null;
-- end;
-- $$ language plpgsql;


-- create or replace function group_chat_after_t() returns trigger
-- as $$
-- begin
--     if (tg_op = 'INSERT') then
--         update topic
--            set last_reply_time = now(),
--                reply_times = reply_times + 1
--          where tid = new.reply_id;
--         return new;
--     end if;
--     return null;
-- end;
-- $$ language plpgsql;


-- create or replace function group_before_t() returns trigger
-- as $$
-- begin
--     if (tg_op = 'DELETE') then
--         delete from group_bulletin where gid = old.gid;
--         delete from group_chat where gid = old.gid;
--         delete from topic where gid = old.gid;
--         delete from group_user where gid = old.gid;
--         delete from group_tag where gid = old.gid;
--         return old;
--     end if;
--     return null;
-- end;
-- $$ language plpgsql;


-- create or replace function group_after_t() returns trigger
-- as $$
-- begin
--     if (tg_op = 'INSERT') then
--         insert into "group_user" (gid, uid, is_leader)
--         values (new.gid, new.uid, true);
--         return new;
--     end if;
--     return null;
-- end;
-- $$ language plpgsql;


-- create or replace function user_before_t() returns trigger
-- as $$
-- begin
--     if (tg_op = 'DELETE') then
--         delete from article_view where uid = old.uid;
--         delete from article_comment where uid = old.uid;
--         delete from article where uid = old.uid;
--         delete from user_title where uid = old.uid;
--         delete from group_bulletin where uid = old.uid;
--         delete from group_chat where uid = old.uid;
--         delete from topic where uid = old.uid;
--         delete from group_user where uid = old.uid;
--         delete from "group" where uid = old.uid;
--         return old;
--     elsif (tg_op = 'UPDATE') then
--         if (new.warnned_times >= 5) then
--             update myuser set is_forbid = true where uid = old.uid;
--         end if;
--         return new;
--     end if;
--     return null;
-- end;
-- $$ language plpgsql;


-- --------------------------------------------------------------------------------
-- -- 触发器
-- --------------------------------------------------------------------------------

-- drop trigger if exists article_before_t on article;
-- create trigger article_before_t before delete or update on article
--    for each row execute procedure article_before_t();

-- drop trigger if exists article_after_t on article;
-- create trigger article_after_t after insert on article
--    for each row execute procedure article_after_t();

-- drop trigger if exists topic_before_t on topic;
-- create trigger topic_before_t before delete on topic
--    for each row execute procedure topic_before_t();

-- drop trigger if exists topic_after_t on topic;
-- create trigger topic_after_t after insert on topic
--    for each row execute procedure topic_after_t();

-- drop trigger if exists group_chat_after_t on group_chat;
-- create trigger group_chat_after_t after insert on group_chat
--    for each row execute procedure group_chat_after_t();

-- drop trigger if exists group_before_t on "group";
-- create trigger group_before_t before delete on "group"
--    for each row execute procedure group_before_t();

-- drop trigger if exists group_after_t on "group";
-- create trigger group_after_t after insert on "group"
--    for each row execute procedure group_after_t();

-- drop trigger if exists user_before_t on myuser;
-- create trigger user_before_t before delete or update on myuser
--    for each row execute procedure user_before_t();
