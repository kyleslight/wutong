/*
 * host     : localhost
 * database : postgresql
 * port     : 5432
 * encoding : utf-8
 */

--------------------------------------------------------------------------------
-- function
--------------------------------------------------------------------------------

create or replace function
get_article_tags(_aid int)
  returns json
as $$
    select array_to_json(array_agg(aj))
      from
        (
            select *
              from article_tag
             where aid = _aid
        ) aj;
$$ language sql;


create or replace function
get_group_sessions(_gid int)
  returns json
as $$
    select array_to_json(array_agg(aj))
      from
        (
            select *
              from
                (
                    select row_to_json(j.*)::text, j.reply_time
                      from
                        (
                            select *
                              from group_topic
                             where gid = _gid
                        ) j
                    union
                    select row_to_json(j.*)::text, j.reply_time
                      from
                        (
                            select *
                              from group_message
                             where gid = _gid
                        ) j
                ) s
             order by s.reply_time
        ) aj;
$$ language sql;

create or replace function
get_article(_aid int)
  returns json
as $$
    select a.*,
           at.tags
      from article a,
           article_tag_baseinfo at
     where a.aid = _aid
       and at.aid = _aid;
$$ language sql;
-- switch_star

create or replace function
get_uid(_account varchar)
  returns int
as $$
    select uid
      from "user"
     where _account = any(array[email, nickname]);
$$ language sql;


create or replace function
get_user_permission(_uid int)
  returns json
as $$
    select row_to_json(j.*)
      from
        (
            select is_activated,
                   is_forbid,
                   is_deleted,
                   is_admin
              from "user"
             where uid = _uid
        ) j;
$$ language sql;


create or replace function
get_user_info(_uid int)
  returns json
as $$
    select row_to_json(j.*)
      from
        (
            select *
              from user_info_v
             where uid = _uid
        ) j;
$$ language sql;


create or replace function
is_user_exists(_email varchar, _nickname varchar, _phone varchar)
  returns int
as $$
    select uid
      from "user"
     where email = _email
        or nickname = _nickname
        or phone = _phone;
$$ language sql;


create or replace function
do_register_user(_email varchar, _nickname varchar, _password varchar)
  returns varchar
as $$
declare
    _uid int;
    _hashuid varchar;
begin
    _hashuid := null;
    select is_user_exists(_email, _nickname, null) into _uid;
    if _uid is null then
        insert into "user"
            (email, nickname, password)
        values
            (_email, _nickname, crypt(_password, gen_salt('bf')))
        returning md5(cast(uid as varchar)) into _hashuid;
    end if;
    return _hashuid;
end;
$$ language plpgsql;


create or replace function
update_user_info(
    _uid int,
    _email varchar,
    _nickname varchar,
    _phone varchar,
    _realname varchar,
    _sex bool,
    _age int,
    _address varchar,
    _intro varchar,
    _motto varchar,
    _avatar varchar)
  returns int
as $$
    update "user"
       set email = _email,
           nickname = _nickname,
           phone = _phone,
           realname = _realname,
           sex = _sex,
           age = _age,
           address = _address,
           intro = _intro,
           motto = _motto,
           avatar = _avatar
     where uid = _uid
    returning uid;
$$ language sql;


create or replace function
do_activate_user(_hashuid varchar)
  returns int
as $$
    update "user"
       set is_activated = true
     where not is_activated
       and _hashuid = md5(cast(uid as varchar))
    returning uid;
$$ language sql;


create or replace function
do_login_user(_account varchar, _password varchar)
  returns int
as $$
    select uid
      from "user"
     where is_activated
       and not is_forbid
       and not is_deleted
       and _account = any(array[email, nickname, phone])
       and password = crypt(_password, password);
$$ language sql;


create or replace function
get_notifications(_uid int, _limit int, _offset int)
  returns json
as $$
    select array_to_json(array_agg(aj))
      from
        (
            select *
              from notification
             where uid = _uid
             limit _limit
            offset _offset
        ) aj;
$$ language sql;


create or replace function
create_notification(
    _uid int,
    _nickname varchar,
    _title varchar,
    _content varchar,
    _type varchar,
    _url varchar)
  returns int
as $$
declare
    _tmp int;
begin
    insert into notification
        (uid, receiver, title, content, type, url)
    values
        (_uid, _nickname, _title, _content, _type, _url)
    returning id into _tmp;
    return _tmp;
end;
$$ language plpgsql;


create or replace function
get_user_groups(_uid int, _limit int, _offset int)
  returns json
as $$
    select array_to_json(array_agg(aj))
      from
        (
            select g.gid, g.name
              from group_user gu,
                   "group" g
             where gu.uid = _uid
               and gu.gid = g.gid
             limit _limit
            offset _offset
        ) aj;
$$ language sql;


create or replace function
get_group_permission(_gid int, _uid int)
  returns json
as $$
    select row_to_json(j.*)
      from
        (
            select *
              from group_user
             where gid = _gid
               and uid = _uid
        ) j;
$$ language sql;


create or replace function
get_group_info(_gid int)
  returns json
as $$
    select row_to_json(j.*)
      from
        (
            select *
              from group_info_v
             where gid = _gid
        ) j;
$$ language sql;


create or replace function
create_group(
    _uid int,
    _name varchar,
    _intro varchar,
    _motto varchar,
    _avatar varchar,
    _banner varchar,
    _is_public bool)
  returns int
as $$
    insert into "group"
        (uid, name, intro, motto, avatar, banner, is_public)
    values
        (_uid, _name, _intro, _motto, _avatar, _banner, _is_public)
    returning gid;
$$ language sql;


create or replace function
join_group(_gid int, _uid int)
  returns int
as $$
    insert into group_user
        (gid, uid)
    select _gid, _uid
     where not exists
        (
            select guid
              from group_user
             where gid = _gid
               and uid = _uid
        )
    returning guid;
$$ language sql;


create or replace function
get_group_tags(_gid int)
  returns json
as $$
    select array_to_json(array_agg(aj))
      from
        (
            select name
              from group_tag
             where gid = _gid
        ) aj;
$$ language sql;


create or replace function
get_group_member_info(_gid int, _uid int)
  returns json
as $$
    select row_to_json(j.*)
      from
        (
            select *
              from group_member_info_v
             where gid = _gid
               and uid = _uid
        ) j;
$$ language sql;


create or replace function
get_group_members(_gid int, _limit int, _offset int)
  returns json
as $$
    select array_to_json(array_agg(aj))
      from
        (
            select *
              from group_member_info_v
             where gid = _gid
             order by guid desc
             limit _limit
            offset _offset
        ) aj;
$$ language sql;


create or replace function
get_group_chats(_gid int, _limit int, _offset int)
  returns json
as $$
    select array_to_json(array_agg(aj))
      from
        (
            select *
              from group_chat_v
             where gid = _gid
             order by id desc
             limit _limit
            offset _offset
        ) aj;
$$ language sql;


create or replace function
get_group_chat(_id int)
  returns json
as $$
    select row_to_json(j.*)
      from
        (
            select *
              from group_chat_v
             where id = _id
        ) j;
$$ language sql;


create or replace function
create_topic(
    _gid int,
    _uid int,
    _title varchar,
    _content varchar,
    _reply_id int)
  returns int
as $$
    insert into topic
        (gid, uid, title, content, reply_id)
    values
        (_gid, _uid, _title, _content, _reply_id)
    returning tid;
$$ language sql;


create or replace function
get_topics(_limit int, _offset int)
  returns json
as $$
    select array_to_json(array_agg(aj))
      from
        (
            select gt.*,
                   g.name as "group_name"
              from group_topic_v gt,
                   "group" g
             where gt.gid = g.gid
             order by last_reply_time desc
             limit _limit
            offset _offset
        ) aj;
$$ language sql;


create or replace function
get_topics_by_tag(_tag varchar, _limit int, _offset int)
  returns json
as $$
    select array_to_json(array_agg(aj))
      from
        (
            select gt.*,
                   g.name as "group_name"
              from group_topic_v gt,
                   "group" g,
                   group_tag g_tag
             where gt.gid = g.gid
               and gt.gid = g_tag.gid
               and g_tag.name = _tag
             order by last_reply_time desc
             limit _limit
            offset _offset
        ) aj;
$$ language sql;


create or replace function
get_group_topics(_gid int, _limit int, _offset int)
  returns json
as $$
    select array_to_json(array_agg(aj))
      from
        (
            select *
              from group_topic_v
             where gid = _gid
             order by tid desc
             limit _limit
            offset _offset
        ) aj;
$$ language sql;


create or replace function
get_user_topics(_uid int, _limit int, _offset int)
  returns json
as $$
    select array_to_json(array_agg(aj))
      from
        (
            select gt.*,
                   g.name as "group_name"
              from group_topic_v gt,
                   "group" g,
                   group_user gu
             where gt.gid = g.gid
               and gu.gid = g.gid
               and gu.uid = _uid
               and gu.is_member
             order by last_reply_time desc
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
              from group_topic_v
             where tid = _tid
        ) j;
$$ language sql;


create or replace function
get_topic_topics(_reply_id int, _limit int, _offset int)
  returns json
as $$
    select array_to_json(array_agg(aj))
      from
        (
            select *
              from group_topic_v
             where reply_id = _reply_id
             order by tid desc
             limit _limit
            offset _offset
        ) aj;
$$ language sql;


create or replace function
get_topic_chats(_reply_id int, _limit int, _offset int)
  returns json
as $$
    select array_to_json(array_agg(aj))
      from
        (
            select *
              from group_chat_v
             where reply_id = _reply_id
             order by id desc
             limit _limit
            offset _offset
        ) aj;
$$ language sql;


create or replace function
create_group_chat(
    _gid int,
    _uid int,
    _content varchar,
    _reply_id int)
  returns int
as $$
    insert into group_chat
        (gid, uid, content, reply_id)
    values
        (_gid, _uid, _content, _reply_id)
    returning id;
$$ language sql;


create or replace function
get_topic_messages(_tid int, _limit int, _offset int)
  returns json
as $$
    select array_to_json(array_agg(aj))
      from
        (
            select *
              from group_message_v
             where reply_id = _tid
             order by last_reply_time desc
             limit _limit
            offset _offset
        ) aj;
$$ language sql;


create or replace function
get_group_message(_message_id int)
  returns json
as $$
    select row_to_json(j.*)
      from
        (
            select *
              from group_message_v
             where id = _message_id
        ) j;
$$ language sql;


create or replace function
get_group_messages(_gid int, _limit int, _offset int)
  returns json
as $$
    select array_to_json(array_agg(aj))
      from
        (
            select *
              from group_message_v
             where gid = _gid
               and reply_id is null
             order by last_reply_time desc
             limit _limit
            offset _offset
        ) aj;
$$ language sql;


create or replace function
get_topic_messages(_tid int, _limit int, _offset int)
  returns json
as $$
    select array_to_json(array_agg(aj))
      from
        (
            select *
              from group_message_v
             where reply_id = _tid
             order by last_reply_time desc
             limit _limit
            offset _offset
        ) aj;
$$ language sql;


create or replace function
get_group_bulletins(_gid int, _limit int, _offset int)
  returns json
as $$
    select array_to_json(array_agg(aj))
      from
        (
            select *
              from group_bulletin_v
             where gid = _gid
             order by id desc
             limit _limit
            offset _offset
        ) aj;
$$ language sql;


create or replace function
create_group_bulletin(
    _gid int,
    _uid int,
    _title varchar,
    _content varchar)
  returns int
as $$
    insert into group_bulletin
        (gid, uid, title, content)
    values
        (_gid, _uid, _title, _content)
    returning id;
$$ language sql;


create or replace function
is_article_author(_aid int, _uid int)
  returns bool
as $$
declare
    _res bool;
begin
    select true
      from article
     where aid = _aid
       and uid = _uid
      into _res;
    if _res is null then
        _res := false;
    end if;
    return _res;
end;
$$ language plpgsql;



create or replace function
get_article_collections(_uid int, _limit int, _offset int)
  returns json
as $$
    select array_to_json(array_agg(aj.*))
      from
        (
            select *,
                   get_article_tags(a.aid) as "tags"
              from article_collection_v a
             where uid = _uid
             order by id desc
             limit _limit
            offset _offset
        ) aj;
$$ language sql;


create or replace function
create_article(
    _uid int,
    _title varchar,
    _mainbody varchar,
    _description varchar default null,
    _suit_for varchar default null,
    _reference varchar default null,
    _series varchar default null,
    _resource varchar default null,
    _is_public int default 2) --'推送'
  returns int
as $$
    insert into article
        (uid, title, mainbody, description, suit_for, reference, series, resource, is_public)
    values
        (_uid, _title, _mainbody, _description, _suit_for, _reference, _series, _resource, _is_public)
    returning aid;
$$ language sql;


create or replace function
create_article_view(_aid int, _uid int, _ip varchar)
  returns int
as $$
    insert into article_view
        (aid, uid, ip)
    select _aid, _uid, _ip
     where not exists
        (
            select uid, ip
              from article_view
             where aid = _aid
               and (uid = _uid or ip = _ip)
        )
    returning id;
$$ language sql;


create or replace function
create_article_collection(_aid int, _uid int)
  returns int
as $$
    insert into article_collection
        (aid, uid)
    select _aid, _uid
     where not
        (
            select is_article_author(_aid, _uid)
        )
    returning id;
$$ language sql;


create or replace function
create_article_score(_aid int, _uid int, _score int)
  returns int
as $$
    insert into article_score
        (aid, uid, score)
    select _aid, _uid, _score
     where not
        (
            select is_article_author(_aid, _uid)
        )
    returning id;
$$ language sql;


create or replace function
count_article_view(_aid int)
  returns bigint
as $$
    select count(aid)
      from article_view
     where aid = _aid
$$ language sql;


create or replace function
count_article_collection(_aid int)
  returns bigint
as $$
    select count(aid)
      from article_collection
     where aid = _aid
$$ language sql;


create or replace function
calc_article_score(_aid int)
  returns numeric
as $$
    select coalesce(avg(score), 0)
      from article_score
     where aid = _aid
$$ language sql;


create or replace function
create_article_tags(_aid int, _tags varchar[])
  returns void
as $$
declare
    _tag varchar;
begin
    foreach _tag in array _tags
    loop
        insert into article_tag
            (aid, name)
        values
            (_aid, _tag);
    end loop;
end;
$$ language plpgsql;


create or replace function
get_article_info(_aid int)
  returns json
as $$
    select row_to_json(j.*)
      from
        (
            select *,
                   (select get_article_tags($1)) as "tags",
                   (select count_article_view($1)) as "views",
                   (select calc_article_score($1)) as "score",
                   (select count_article_collection($1)) as "collections"
              from article_info_v
             where aid = _aid
        ) j;
$$ language sql;


create or replace function
get_articles(_limit int, _offset int)
  returns json
as $$
    select array_to_json(array_agg(aj.*))
      from
        (
            select a.aid,
                   a.title,
                   a.author,
                   a.avatar,
                   a.submit_time,
                   a.description,
                   (select get_article_tags(a.aid)) as "tags"
              from article_info_v a
             where a.is_public = 2
               and not a.is_deleted
             order by a.aid desc
             limit _limit
            offset _offset
        ) aj;
$$ language sql;


create or replace function
get_articles_by_tag(_tag varchar, _limit int, _offset int)
  returns json
as $$
    select array_to_json(array_agg(aj.*))
      from
        (
            select a.aid,
                   a.title,
                   a.author,
                   a.avatar,
                   a.submit_time,
                   a.description,
                   (select get_article_tags(a.aid)) as "tags"
              from article_info_v a,
                   article_tag at
             where a.is_public = 2
               and not a.is_deleted
               and a.aid = at.aid
               and at.name = _tag
             order by a.aid desc
             limit _limit
            offset _offset
        ) aj;
$$ language sql;


create or replace function
get_comment(_id int)
  returns json
as $$
    select row_to_json(j.*)
      from
        (
            select *
              from article_comment_v
             where id = _id
        ) j;
$$ language sql;


create or replace function
get_side_comments(_aid int)
  returns json
as $$
    select array_to_json(array_agg(aj.*))
      from
        (
            select *
              from article_comment_v
             where aid = _aid
               and is_side
        ) aj;
$$ language sql;


create or replace function
get_bottom_comments(_aid int, _limit int, _offset int)
  returns json
as $$
    select array_to_json(array_agg(aj.*))
      from
        (
            select *
              from article_comment_v
             where aid = _aid
               and is_side = false
             order by id
             limit _limit
            offset _offset
        ) aj;
$$ language sql;


create or replace function
create_side_comment(
    _aid int,
    _uid int,
    _content varchar,
    _paragraph_id varchar)
  returns int
as $$
declare
    _tmp int;
begin
    select max(floor) + 1
      from article_comment
     where aid = _aid
       and is_side
      into _tmp;
    if _tmp is null then
        _tmp := 1;
    end if;

    insert into article_comment
        (aid, uid, content, paragraph_id, is_side, floor)
    values
        (_aid, _uid, _content, _paragraph_id, true, _tmp)
    returning id into _tmp;
    return _tmp;
end;
$$ language plpgsql;


create or replace function
create_bottom_comment(_aid int, _uid int, _content varchar)
  returns int
as $$
declare
    _tmp int;
begin
    select max(floor) + 1
      from article_comment
     where aid = _aid
       and is_side = false
      into _tmp;
    if _tmp is null then
        _tmp := 1;
    end if;

    insert into article_comment
        (aid, uid, content, floor)
    values
        (_aid, _uid, _content, _tmp)
    returning id into _tmp;
    return _tmp;
end;
$$ language plpgsql;


create or replace function
get_search_opus(_aid int)
  returns json
as $$
    select row_to_json(j.*)
      from
        (
            select *,
                   (select get_article_tags(id)) as "tags"
              from search_article_v
             where id = _aid
        ) j;
$$ language sql;


create or replace function
get_search_group(_gid int)
  returns json
as $$
    select row_to_json(j.*)
      from
        (
            select *,
                   (select get_group_tags(id)) as "tags"
              from search_group_v
             where id = _gid
        ) j;
$$ language sql;


create or replace function
get_search_user(_uid int)
  returns json
as $$
    select row_to_json(j.*)
      from
        (
            select *
              from search_user_v
             where id = _uid
        ) j;
$$ language sql;


create or replace function article_before_t() returns trigger
as $$
begin
    if (tg_op = 'DELETE') then
        delete from article_history where aid = old.aid;
        delete from article_honor where aid = old.aid;
        delete from article_appositeness where aid = old.aid;
        delete from article_tag where aid = old.aid;
        delete from article_comment where aid = old.aid;
        delete from article_view where aid = old.aid;
        delete from article_user where aid = old.aid;
        return old;
    elsif (tg_op = 'UPDATE') then
        insert into article_history (
            aid, title, mainbody,
            description, reference, series, resource)
        select aid, title,
               mainbody,
               description, reference,
               series, resource
          from article
         where aid = old.aid;
        return new;
    end if;
    return null;
end;
$$ language plpgsql;


create or replace function article_after_t() returns trigger
as $$
begin
    if (tg_op = 'INSERT') then
        update article set last_modify_time = submit_time where aid = new.aid;
        return new;
    end if;
    return null;
end;
$$ language plpgsql;


create or replace function topic_before_t() returns trigger
as $$
begin
    if (tg_op = 'DELETE') then
        delete from group_chat where reply_id = old.tid;
        delete from topic where reply_id = old.tid;
        return old;
    end if;
    return null;
end;
$$ language plpgsql;


create or replace function topic_after_t() returns trigger
as $$
begin
    if (tg_op = 'INSERT') then
        update topic
           set last_reply_time = now(),
               reply_times = reply_times + 1
         where tid = new.tid;
        return new;
    end if;
    return null;
end;
$$ language plpgsql;


create or replace function group_chat_after_t() returns trigger
as $$
begin
    if (tg_op = 'INSERT') then
        update topic
           set last_reply_time = now(),
               reply_times = reply_times + 1
         where tid = new.reply_id;
        return new;
    end if;
    return null;
end;
$$ language plpgsql;


create or replace function group_before_t() returns trigger
as $$
begin
    if (tg_op = 'DELETE') then
        delete from group_bulletin where gid = old.gid;
        delete from group_chat where gid = old.gid;
        delete from topic where gid = old.gid;
        delete from group_user where gid = old.gid;
        delete from group_tag where gid = old.gid;
        return old;
    end if;
    return null;
end;
$$ language plpgsql;


create or replace function group_after_t() returns trigger
as $$
begin
    if (tg_op = 'INSERT') then
        insert into "group_user" (gid, uid, is_leader)
        values (new.gid, new.uid, true);
        return new;
    end if;
    return null;
end;
$$ language plpgsql;


create or replace function user_before_t() returns trigger
as $$
begin
    if (tg_op = 'DELETE') then
        delete from article_view where uid = old.uid;
        delete from article_comment where uid = old.uid;
        delete from article where uid = old.uid;
        delete from user_title where uid = old.uid;
        delete from group_bulletin where uid = old.uid;
        delete from group_chat where uid = old.uid;
        delete from topic where uid = old.uid;
        delete from group_user where uid = old.uid;
        delete from "group" where uid = old.uid;
        return old;
    elsif (tg_op = 'UPDATE') then
        if (new.warnned_times >= 5) then
            update "user" set is_forbid = true where uid = old.uid;
        end if;
        return new;
    end if;
    return null;
end;
$$ language plpgsql;


--------------------------------------------------------------------------------
-- 触发器
--------------------------------------------------------------------------------

drop trigger if exists article_before_t on article;
create trigger article_before_t before delete or update on article
   for each row execute procedure article_before_t();

drop trigger if exists article_after_t on article;
create trigger article_after_t after insert on article
   for each row execute procedure article_after_t();

drop trigger if exists topic_before_t on topic;
create trigger topic_before_t before delete on topic
   for each row execute procedure topic_before_t();

drop trigger if exists topic_after_t on topic;
create trigger topic_after_t after insert on topic
   for each row execute procedure topic_after_t();

drop trigger if exists group_chat_after_t on group_chat;
create trigger group_chat_after_t after insert on group_chat
   for each row execute procedure group_chat_after_t();

drop trigger if exists group_before_t on "group";
create trigger group_before_t before delete on "group"
   for each row execute procedure group_before_t();

drop trigger if exists group_after_t on "group";
create trigger group_after_t after insert on "group"
   for each row execute procedure group_after_t();

drop trigger if exists user_before_t on "user";
create trigger user_before_t before delete or update on "user"
   for each row execute procedure user_before_t();
