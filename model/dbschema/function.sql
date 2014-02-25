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
update_user_collection(_uid int, _type sort, _relevant_id int) returns void
as $$
begin
  perform id
     from user_collection
    where uid = _uid
      and relevant_id = _relevant_id
      and type = _type;

  if FOUND then
    delete from user_collection
          where uid = _uid
            and relevant_id = _relevant_id
            and type = _type;
  else
    insert into user_collection
        (uid, type, relevant_id)
    values
        (_uid, _type, _relevant_id);
  end if;
end;
$$ language plpgsql;

create or replace function
has_user_collected(_uid int, _type sort, _relevant_id int) returns bool
as $$
begin
  perform *
     from user_collection
    where uid = _uid
      and relevant_id = _relevant_id
      and type = _type;

  if FOUND then
    return true;
  else
    return false;
  end if;
end;
$$ language plpgsql;

create or replace function
get_user_collections(_uid int, _type sort, _limit int, _offset int) returns json
as $$
declare
  _idname text;
  _tabname text;
  _tmp json;
begin
  case _type
    when '1' then
      _tabname := 'article_base';
      _idname := 'aid';
    when '2' then
      _tabname := 'group_topic';
      _idname := 'tid';
    else
      return null;
  end case;

  execute '
  select array_to_json(array_agg(aj))
    from
      (
         select item.*,
                uc.create_time
           from ' || _tabname::regclass || ' as "item",
                user_collection uc
          where uc.relevant_id = item.' || quote_ident(_idname) || '
            and uc.uid = ' || _uid || '
            and uc.type = ' || quote_literal(_type) || '
           order by uc.id desc
           limit ' || _limit || '
          offset ' || _offset || '
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
get_mygroups(_uid int, _limit int, _offset int) returns json
as $$
  select array_to_json(array_agg(aj.*))
    from
      (
         select *
           from group_base
          where gid in
             (
                select gid
                  from group_member
                 where uid = _uid
                   and position_level = '4'
                 order by join_time desc
                 limit _limit
                offset _offset
             )
      ) aj;
$$ language sql;


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
is_article_author(_aid int, _uid int) returns bool
as $$
begin
  perform *
     from article
    where aid = _aid
      and uid = _uid;

  if FOUND then
    return true;
  else
    return false;
  end if;
end;
$$ language plpgsql;

create or replace function
get_article(_aid int) returns json
as $$
  select row_to_json(j.*)
    from
      (
         select a.*,
                c.coeditors
           from article_show a,
                article_coeditor_base c
          where a.aid = _aid
            and a.aid = c.aid
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
    _reply_id int) returns int
as $$
  insert into article_bottom_comment
      (aid, uid, reply_id, content, rank)
  values
      (_aid, _uid, _reply_id, _content, (select COALESCE(max(rank), 0) + 1
                                           from article_bottom_comment
                                          where aid = _aid))
  returning id;
$$ language sql;

create or replace function
create_side_comment(
    _aid int,
    _uid int,
    _content text,
    _paragraph_id text) returns int
as $$
  insert into article_side_comment
      (aid, uid, content, paragraph_id)
  values
      (_aid, _uid, _content, _paragraph_id)
  returning id;
$$ language sql;

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
     from user_collection
    where type = '1'
      and relevant_id = _aid
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
update_article_myscore(_aid int, _uid int, _score int) returns int
as $$
declare
    _tmp int;
begin
  select id into _tmp
    from article_score
   where aid = _aid
     and uid = _uid;

  if _tmp is not null then
    update article_score
       set score = _score
     where aid = _aid
       and uid = _uid
    returning id into _tmp;
  else
    insert into article_score
        (aid, uid, score)
    values
        (_aid, _uid, _score)
    returning id into _tmp;
  end if;

  return _tmp;
end;
$$ language plpgsql;

create or replace function
is_group_member(_gid int, _uid int) returns bool
as $$
  select position_level > '1'
    from group_member
   where gid = _gid
     and uid = _uid;
$$ language sql;

create or replace function
is_group_visiable(_gid int, _uid int) returns bool
as $$
declare
  _tmp bool;
begin
  select public_level > '1' into _tmp
    from mygroup
   where gid = _gid;

  if not _tmp then
    select is_group_member(_gid, _uid) into _tmp;
  end if;
  return _tmp;
end;
$$ language plpgsql;

create or replace function
get_group_homepage(_gid int) returns json
as $$
declare
  _rank int;
  _tmp json;
begin
  select row_to_json(j.*) into _tmp
    from
      (
         select *,
                COALESCE((
                  select avg(score)
                    from article_score
                   where aid in
                      (
                         select aid
                           from article
                          where uid in
                             (
                                select uid
                                  from group_member
                                 where gid = _gid
                             )
                      )), 0) as "avg_article_score"
           from group_show
          where gid = _gid
      ) j;

  return _tmp;
end;
$$ language plpgsql;

create or replace function
get_topic_homepage(_tid int) returns json
as $$
declare
    _tmp json;
begin
  select row_to_json(j.*) into _tmp
    from
      (
         select *
           from group_topic_show
          where tid = _tid
      ) j;
  return _tmp;
end;
$$ language plpgsql;

create or replace function
get_group_members(_gid int, _limit int, _offset int)
  returns json
as $$
    select array_to_json(array_agg(aj))
      from
        (
           select *
             from group_member_show
            where gid = _gid
            order by join_time desc
            limit _limit
           offset _offset
        ) aj;
$$ language sql;

create or replace function
get_group_articles(_gid int, _limit int, _offset int)
  returns json
as $$
    select array_to_json(array_agg(aj))
      from
        (
           select a.*
             from group_member gm,
                  article_base a
            where gm.gid = _gid
              and gm.uid = a.uid
              and a.public_level > '2'
            order by a.modify_time desc
            limit _limit
           offset _offset
        ) aj;
$$ language sql;

create or replace function
get_group_sessions(_gid int, _anchor_id int, _limit int)
  returns json
as $$
  select array_to_json(array_agg(aj.session))
    from
      (
         select session
           from
             (
                select row_to_json(j.*)::text as "session", reply_time
                  from group_topic_base j
                 where gid = _gid
                   and anchor_id > _anchor_id
                 union
                select row_to_json(j.*)::text as "session", reply_time
                  from group_message_show j
                 where gid = _gid
                   and anchor_id > _anchor_id
             ) s
          order by s.reply_time desc
          limit _limit
      ) aj;
$$ language sql;

create or replace function
get_topic_sessions(_tid int, _anchor_id int, _limit int)
  returns json
as $$
  select array_to_json(array_agg(aj.session))
    from
      (
         select session
           from
             (
                select row_to_json(j.*)::text as "session", reply_time
                  from group_topic_base j
                 where father_id = _tid
                   and anchor_id > _anchor_id
                 union
                select row_to_json(j.*)::text as "session", reply_time
                  from group_message_show j
                 where tid = _tid
                   and anchor_id > _anchor_id
             ) s
          order by s.reply_time desc
          limit _limit
      ) aj;
$$ language sql;

create or replace function
get_user_groups(_uid int, _limit int, _offset int)
  returns json
as $$
  select array_to_json(array_agg(aj.*))
    from
      (
         select *
           from group_base
          where gid in
             (
                select gid
                  from group_member
                 where uid = _uid
                   and position_level > '1'
                 order by join_time desc
                 limit _limit
                offset _offset
             )
      ) aj;
$$ language sql;

create or replace function
get_mygroup_topics(_uid int, _limit int, _offset int)
  returns json
as $$
  select array_to_json(array_agg(aj.*))
    from
      (
         select t.*,
                g.name as "group_name"
           from group_topic_base t,
                mygroup g
          where t.gid = g.gid
            and t.gid in (
                select gid
                  from group_member
                 where uid = _uid
                   and position_level > '1')
          order by t.reply_time desc
          limit _limit
         offset _offset
      ) aj;
$$ language sql;

create or replace function
get_browse_topics(_limit int, _offset int)
  returns json
as $$
  select array_to_json(array_agg(aj.*))
    from
      (
         select t.*,
                g.name as "group_name"
           from group_topic_base t,
                mygroup g
          where t.gid = g.gid
          order by t.reply_time desc
          limit _limit
         offset _offset
      ) aj;
$$ language sql;

create or replace function
get_topic(_tid int)
  returns json
as $$
  select row_to_json(j.*)
    from
      (
         select *
           from group_topic_base
          where tid = _tid
      ) j;
$$ language sql;

create or replace function
get_topics(_limit int, _offset int)
  returns json
as $$
  select array_to_json(array_agg(aj.*))
    from
      (
         select *
           from group_topic_base
          order by reply_time desc
          limit _limit
         offset _offset
      ) aj;
$$ language sql;

create or replace function
create_group(_uid int, _name text, _intro text, _public_level sort)
  returns int
as $$
declare
  _tmp int;
begin
  insert into mygroup
      (uid, name, intro, public_level)
  values
      (_uid, _name, _intro, _public_level)
  returning gid into _tmp;

  insert into group_member
      (uid, gid, position_level)
  values
      (_uid, _tmp, '4');

  return _tmp;
end;
$$ language plpgsql;

create or replace function
update_group_tags(_gid int, _tags text[]) returns void
as $$
declare
  _tag text;
begin
  PERFORM id
     from group_tag
    where gid = _gid;
  if FOUND then
    delete from group_tag where gid = _gid;
  end if;
  foreach _tag in array _tags
  loop
    insert into group_tag (gid, content) values (_gid, _tag);
  end loop;
end;
$$ language plpgsql;

create or replace function
join_group(_gid int, _uid int) returns int
as $$
declare
  _tmp sort;
begin
  select position_level into _tmp
    from group_member
   where gid = _gid
     and uid = _uid;

  if _tmp is null then
    select public_level into _tmp
      from mygroup
     where gid = _gid;
    if _tmp > '1' then
      _tmp := '2';
    else
      _tmp := '1';
    end if;

    -- TODO: send message to group leader
    insert into group_member
        (gid, uid, position_level)
    values
        (_gid, _uid, _tmp);
    return 0;
  elsif _tmp = '1' then
    return 1;
  else
    return 2;
  end if;
end;
$$ language plpgsql;

create or replace function
create_group_message(_gid int, _uid int, _content text, _tid int) returns json
as $$
declare
  _tmp int;
begin
    insert into group_message
        (gid, uid, content, tid)
    values
        (_gid, _uid, _content, _tid)
    returning id into _tmp;
    if _tid is not null then
      update group_topic
         set reply_time = now()
       where tid = _tid;
    end if;

    return (select row_to_json(j.*)
              from group_message_show j
             where id = _tmp);
end;
$$ language plpgsql;

create or replace function
create_group_topic(_gid int, _uid int, _title text, _content text, _father_id int) returns json
as $$
declare
  _tmp int;
begin
    insert into group_topic
        (gid, uid, title, content, father_id, ancestor_id)
    values
        (_gid, _uid, _title, _content, _father_id, (select father_id
                                                      from group_topic
                                                     where gid = _gid
                                                       and tid = _father_id))
    returning tid into _tmp;
    if _tid is not null then
      update group_topic
         set reply_time = now()
       where tid = _father_id;
    end if;

    return (select row_to_json(j.*)
              from group_topic_base j
             where tid = _tmp);
end;
$$ language plpgsql;
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
