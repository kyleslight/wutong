/*
 Host     : localhost
 Database : PostgreSQL
 Port     : 5432
 Encoding : utf-8
*/

--------------------------------------------------------------------------------
-- function
--------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION get_uid(_account varchar)
  RETURNS integer
AS $$
    SELECT uid
      FROM "user"
     WHERE email = $1
        OR penname = $1
        OR phone = $1;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_user_permission(_uid integer)
  RETURNS json
AS $$
    SELECT row_to_json(j.*)
      FROM (
            SELECT is_activated, is_forbid,
                   is_deleted, is_admin
              FROM "user"
             WHERE uid = $1
        ) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_user_info(_uid integer)
  RETURNS json
AS $$
    SELECT row_to_json(j.*)
      FROM (
            SELECT *
              FROM user_info_v
             WHERE uid = $1
        ) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION is_user_exists(
    _email varchar,
    _penname varchar,
    _phone varchar)
  RETURNS integer
AS $$
  SELECT uid
    FROM "user"
   WHERE email = $1
      OR penname = $2
      OR phone = $3;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION do_register_user(
    _email varchar,
    _penname varchar,
    _password varchar)
  RETURNS varchar
AS $$
DECLARE
    _uid integer;
    _hashuid varchar;
BEGIN
    SELECT is_user_exists($1, $2, NULL) INTO _uid;
    IF _uid IS NOT NULL THEN
        RETURN NULL;
    END IF;

    INSERT INTO "user" (
        email, penname, password)
    VALUES (
        $1, $2, crypt($3, gen_salt('bf')))
    RETURNING md5(CAST(uid AS varchar))
    INTO _hashuid;
    RETURN _hashuid;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION update_user_info(
  _uid integer,
  _email varchar,
  _penname varchar,
  _phone varchar,
  _realname varchar,
  _sex bool,
  _age integer,
  _address varchar,
  _intro varchar,
  _motto varchar,
  _avatar varchar)
  RETURNS integer
AS $$
  UPDATE "user"
     SET email = _email,
         penname = _penname,
         phone = _phone,
         realname = _realname,
         sex = _sex,
         age = _age,
         address = _address,
         intro = _intro,
         motto = _motto,
         avatar = _avatar
   WHERE uid = _uid
   RETURNING uid;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION do_activate_user(_hashuid varchar)
  RETURNS integer
AS $$
  UPDATE "user"
     SET is_activated = true
   WHERE is_activated = false
     AND $1 = md5(CAST(uid AS varchar))
   RETURNING uid;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION do_login_user(
    _account varchar,
    _password varchar)
  RETURNS integer
AS $$
    SELECT uid
      FROM "user"
     WHERE is_activated
       AND NOT is_forbid
       AND NOT is_deleted
       AND (
            email = $1
         OR penname = $1
         OR phone = $1)
       AND password = crypt($2, password);
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_notifications(
    _uid integer,
    _limit integer,
    _offset integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(aj))
      FROM (
            SELECT *
              FROM notification
             WHERE uid = $1
             LIMIT $2
            OFFSET $3
        ) aj;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION create_notification(
    _uid integer,
    _penname varchar,
    _title varchar,
    _content varchar,
    _type varchar,
    _url varchar)
  RETURNS integer
AS $$
DECLARE
    _tmp integer;
BEGIN
    INSERT INTO notification (uid, receiver, title, content, type, url)
    VALUES ($1, $2, $3, $4, $5, $6)
    RETURNING id
    INTO _tmp;
    RETURN _tmp;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_user_groups(
    _uid integer,
    _limit integer,
    _offset integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(aj))
      FROM (
            SELECT g.gid, g.name
              FROM group_user gu,
                   "group" g
             WHERE gu.uid = $1
               AND gu.gid = g.gid
             LIMIT $2
            OFFSET $3
        ) aj;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_group_permission(
    _gid integer,
    _uid integer)
  RETURNS json
AS $$
    SELECT row_to_json(j.*)
      FROM (
            SELECT *
              FROM group_user
             WHERE gid = $1 AND uid = $2
        ) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_group_info(gid integer)
  RETURNS json
AS $$
    SELECT row_to_json(j.*)
      FROM (
            SELECT *
              FROM group_info_v
             WHERE gid = $1
        ) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION create_group(
    uid integer,
    name varchar,
    intro varchar DEFAULT NULL,
    motto varchar DEFAULT NULL,
    avatar varchar DEFAULT NULL,
    banner varchar DEFAULT NULL,
    is_public bool DEFAULT true)
  RETURNS integer
AS $$
    INSERT INTO "group" (
        uid, name, intro, motto,
        avatar, banner, is_public)
    VALUES (
        uid, name, intro, motto,
        avatar, banner, is_public)
    RETURNING gid;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION join_group(
    _gid integer,
    _uid integer)
  RETURNS integer
AS $$
    INSERT INTO group_user (gid, uid)
    SELECT $1, $2
     WHERE NOT EXISTS(
               SELECT guid
                 FROM group_user
                WHERE gid = $1
                  AND uid = $2
          )
    RETURNING guid;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_group_dynamics(_uid integer)
  RETURNS json
AS $$
    -- TODO
    SELECT array_to_json(array_agg(aj.*))
      FROM (
            SELECT *
              FROM group_topic_v
             WHERE uid = $1
        ) aj;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_group_member_info(
    _gid integer,
    _uid integer)
  RETURNS json
AS $$
    SELECT row_to_json(j.*)
      FROM (
            SELECT *
              FROM group_member_info_v
             WHERE gid = $1
               AND uid = $2
        ) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_group_members(
    _gid integer,
    _limit integer,
    _offset integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(aj))
      FROM (
            SELECT *
              FROM group_member_info_v
             WHERE gid = $1
             ORDER BY guid DESC
             LIMIT $2
            OFFSET $3
         ) aj;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_group_chats(
    _gid integer,
    _limit integer,
    _offset integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(aj))
      FROM (
            SELECT *
              FROM group_chat_v
             WHERE gid = $1
             ORDER BY id DESC
             LIMIT $2
            OFFSET $3
        ) aj;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_group_chat(
    _id integer)
  RETURNS json
AS $$
    SELECT row_to_json(j.*)
      FROM (
            SELECT *
              FROM group_chat_v
             WHERE id = $1
        ) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION create_topic(
    _gid integer,
    _uid integer,
    _title varchar,
    _content varchar,
    _reply_id integer)
  RETURNS integer
AS $$
    INSERT INTO topic (
        gid, uid, title, content, reply_id)
    VALUES ($1, $2, $3, $4, $5)
    RETURNING tid;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_topics(
    _gid integer,
    _limit integer,
    _offset integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(j))
      FROM (
            SELECT *
              FROM group_topic_v
             WHERE gid = $1
             ORDER BY tid DESC
             LIMIT $2
            OFFSET $3
        ) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_recent_topics(
    _limit integer,
    _offset integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(j))
      FROM (
            SELECT gt.*,
                   g.name as "group_name"
              FROM group_topic_v gt,
                   "group" g
             WHERE gt.gid = g.gid
             ORDER BY last_reply_time DESC
             LIMIT $1
            OFFSET $2
        ) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_user_recent_group_topics(
    _uid integer,
    _limit integer,
    _offset integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(j))
      FROM (
            SELECT gt.*,
                   g.name as "group_name"
              FROM group_topic_v gt,
                   "group" g,
                   group_user gu
             WHERE gt.gid = g.gid
               AND gu.gid = g.gid
               AND gu.uid = $1
               AND gu.is_member
             ORDER BY last_reply_time DESC
             LIMIT $2
            OFFSET $3
        ) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_topic(_tid integer)
  RETURNS json
AS $$
    SELECT row_to_json(j.*)
      FROM (
            SELECT *
              FROM group_topic_v
             WHERE tid = $1
        ) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_topic_topics(
    _reply_id integer,
    _limit integer,
    _offset integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(j))
      FROM (
            SELECT *
              FROM group_topic_v
             WHERE reply_id = $1
             ORDER BY tid DESC
             LIMIT $2
            OFFSET $3) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_topic_chats(
    _reply_id integer,
    _limit integer,
    _offset integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(j))
      FROM (
            SELECT *
              FROM group_chat_v
             WHERE reply_id = $1
             ORDER BY id DESC
             LIMIT $2
            OFFSET $3) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION create_group_chat(
    _gid integer,
    _uid integer,
    content varchar,
    reply_id integer)
  RETURNS integer
AS $$
    INSERT INTO group_chat (
        gid, uid, content, reply_id)
    VALUES ($1, $2, $3, $4)
    RETURNING id;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_topic_messages(
    _topic_id integer,
    _limit integer,
    _offset integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(j))
      FROM (
            SELECT *
              FROM group_message_v
             WHERE reply_id = $1
             ORDER BY last_reply_time DESC
             LIMIT $2
            OFFSET $3) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_group_message(_msg_id integer)
  RETURNS json
AS $$
    SELECT row_to_json(j.*)
      FROM (
            SELECT *
              FROM group_message_v
             WHERE id = $1) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_group_messages(
    _group_id integer,
    _limit integer,
    _offset integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(j))
      FROM (
            SELECT *
              FROM group_message_v
             WHERE gid = $1
               AND reply_id IS NULL
             ORDER BY last_reply_time DESC
             LIMIT $2
            OFFSET $3) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_topic_messages(
    _topic_id integer,
    _limit integer,
    _offset integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(j))
      FROM (
            SELECT *
              FROM group_message_v
             WHERE reply_id = $1
             ORDER BY last_reply_time DESC
             LIMIT $2
            OFFSET $3) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_group_bulletins(
    _gid integer,
    _limit integer,
    _offset integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(j))
      FROM (
            SELECT *
              FROM group_bulletin_v
             WHERE gid = $1
             ORDER BY id DESC
             LIMIT $2
            OFFSET $3
        ) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION create_group_bulletin(
    _gid integer,
    _uid integer,
    _title varchar,
    _content varchar)
  RETURNS integer
AS $$
    INSERT INTO group_bulletin (
        gid, uid, title, content)
    VALUES ($1, $2, $3, $4)
    RETURNING id;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION is_article_author(
  _aid integer,
  _uid integer)
  RETURNS bool
AS $$
    SELECT CASE COALESCE(uid, 0)
           WHEN 0
           THEN false
           ELSE true
            END
      FROM article
     WHERE aid = _aid
       AND uid = _uid;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_article_collections(
    _uid integer,
    _limit integer,
    _offset integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(aj.*))
      FROM (
            SELECT *
              FROM article_collection_v
             WHERE uid = $1
             ORDER BY id
             LIMIT $2
            OFFSET $3
         ) aj;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION create_article(
    _uid integer,
    _title varchar,
    _mainbody varchar,
    _description varchar DEFAULT NULL,
    _suit_for varchar DEFAULT NULL,
    _reference varchar DEFAULT NULL,
    _series varchar DEFAULT NULL,
    _resource varchar DEFAULT NULL,
    _is_public integer DEFAULT 2) --'推送'
  RETURNS integer
AS $$
    INSERT INTO article (
        uid, title, mainbody,
        description, suit_for, reference,
        series, resource, is_public
    )
    VALUES (
        _uid, _title, _mainbody,
        _description, _suit_for, _reference,
        _series, _resource, _is_public
    )
    RETURNING aid;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION create_article_view(
  _aid integer,
  _uid integer,
  _ip varchar)
  RETURNS integer
AS $$
    INSERT INTO article_view
                (aid, uid, ip)
    SELECT $1, $2, $3
     WHERE NOT EXISTS (
               SELECT uid, ip
                 FROM article_view
                WHERE aid = $1
                  AND (uid = $2 OR ip = $3)
          )
    RETURNING id;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION create_article_collection(
  _aid integer,
  _uid integer)
  RETURNS integer
AS $$
    INSERT INTO article_collection
                (aid, uid)
    SELECT _aid, _uid
     WHERE NOT (SELECT is_article_author(_aid, _uid))
    RETURNING id;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION create_article_score(
  _aid integer,
  _uid integer,
  _score integer)
  RETURNS integer
AS $$
    INSERT INTO article_score
                (aid, uid, score)
    SELECT _aid, _uid, _score
     WHERE NOT (SELECT is_article_author(_aid, _uid))
    RETURNING id;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION count_article_view(_aid integer)
  RETURNS bigint
AS $$
    SELECT count(aid)
      FROM article_view
     WHERE aid = $1
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION count_article_collection(_aid integer)
  RETURNS bigint
AS $$
    SELECT count(aid)
      FROM article_collection
     WHERE aid = $1
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION calc_article_score(_aid integer)
  RETURNS numeric
AS $$
    SELECT COALESCE(avg(score), 0)
      FROM article_score
     WHERE aid = $1
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION create_article_tags(
  _aid integer,
  _tags varchar[])
  RETURNS void
AS $$
DECLARE
    _tag varchar;
BEGIN
    FOREACH _tag IN ARRAY _tags
    LOOP
        INSERT INTO article_tag (aid, name)
        VALUES ($1, _tag);
    END LOOP;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_article_tags(_aid integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(aj))
      FROM (
            SELECT name
              FROM article_tag
             WHERE aid = $1
        ) aj;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_article_info(_aid integer)
  RETURNS json
AS $$
    SELECT row_to_json(j.*)
      FROM (
            SELECT *,
                   (SELECT get_article_tags($1)) AS "tags",
                   (SELECT count_article_view($1)) AS "views",
                   (SELECT calc_article_score($1)) AS "score",
                   (SELECT count_article_collection($1)) AS "collections"
              FROM article_info_v
             WHERE aid = $1
        ) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_article_list(
    _sort varchar,
    _limit integer,
    _offset integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(aj.*))
      FROM (
            SELECT a.aid,
                   a.title,
                   a.author,
                   a.avatar,
                   a.submit_time,
                   a.description,
                   (SELECT get_article_tags(a.aid)) AS "tags"
              FROM article_info_v a
             WHERE is_public = 2
             ORDER BY a.aid DESC
         ) aj;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_comment(
    _comment_id integer)
  RETURNS json
AS $$
    SELECT row_to_json(j.*)
      FROM (
            SELECT *
              FROM article_comment_v
             WHERE id = $1
         ) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_side_comments(
    _aid integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(aj.*))
      FROM (
            SELECT *
              FROM article_comment_v
             WHERE aid = $1
               AND is_side
         ) aj;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_bottom_comments(
    _aid integer,
    _limit integer,
    _offset integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(aj.*))
      FROM (
            SELECT *
              FROM article_comment_v
             WHERE aid = $1
               AND is_side = false
             ORDER BY id
             LIMIT $2
            OFFSET $3
         ) aj;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION create_side_comment(
    _aid integer,
    _uid integer,
    _content varchar,
    _paragraph_id varchar)
  RETURNS integer
AS $$
DECLARE
    _tmp integer;
BEGIN
    SELECT max(floor) + 1
      FROM article_comment
     WHERE aid = $1
       AND is_side
      INTO _tmp;
    IF _tmp IS NULL THEN
        _tmp := 1;
    END IF;

    INSERT INTO article_comment (
        aid, uid, content,
        paragraph_id, is_side,
        floor)
    VALUES (
        $1, $2, $3,
        $4, true,
        _tmp)
    RETURNING id
    INTO _tmp;
    RETURN _tmp;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION create_bottom_comment(
    _aid integer,
    _uid integer,
    _content varchar)
  RETURNS integer
AS $$
DECLARE
    _tmp integer;
BEGIN
    SELECT max(floor) + 1
      FROM article_comment
     WHERE aid = $1
       AND is_side = false
      INTO _tmp;
    IF _tmp IS NULL THEN
        _tmp := 1;
    END IF;

    INSERT INTO article_comment (aid, uid, content, floor)
    VALUES ($1, $2, $3, _tmp)
    RETURNING id
    INTO _tmp;
    RETURN _tmp;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION article_before_t()
  RETURNS trigger
AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        DELETE FROM article_history WHERE aid = OLD.aid;
        DELETE FROM article_honor WHERE aid = OLD.aid;
        DELETE FROM article_appositeness WHERE aid = OLD.aid;
        DELETE FROM article_tag WHERE aid = OLD.aid;
        DELETE FROM article_comment WHERE aid = OLD.aid;
        DELETE FROM article_view WHERE aid = OLD.aid;
        DELETE FROM article_user WHERE aid = OLD.aid;
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO article_history (
            aid, title, mainbody,
            description, reference, series, resource)
        SELECT aid, title,
               mainbody,
               description, reference,
               series, resource
          FROM article
         WHERE aid = OLD.aid;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION topic_before_t()
  RETURNS trigger
AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        DELETE FROM group_chat WHERE reply_id = OLD.tid;
        DELETE FROM topic WHERE reply_id = OLD.tid;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION topic_after_t()
  RETURNS trigger
AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        UPDATE topic
           SET last_reply_time = now(),
               reply_times = reply_times + 1
         WHERE tid = NEW.tid;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION group_chat_after_t()
  RETURNS trigger
AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        UPDATE topic
           SET last_reply_time = now(),
               reply_times = reply_times + 1
         WHERE tid = NEW.reply_id;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION group_before_t()
  RETURNS trigger
AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        DELETE FROM group_bulletin WHERE gid = OLD.gid;
        DELETE FROM group_chat WHERE gid = OLD.gid;
        DELETE FROM topic WHERE gid = OLD.gid;
        DELETE FROM group_user WHERE gid = OLD.gid;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION group_after_t()
  RETURNS trigger
AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO "group_user" (gid, uid, is_leader)
        VALUES (NEW.gid, NEW.uid, true);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION user_before_t()
  RETURNS trigger
AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        DELETE FROM article_view WHERE uid = OLD.uid;
        DELETE FROM article_comment WHERE uid = OLD.uid;
        DELETE FROM article WHERE uid = OLD.uid;
        DELETE FROM user_title WHERE uid = OLD.uid;
        DELETE FROM group_bulletin WHERE uid = OLD.uid;
        DELETE FROM group_chat WHERE uid = OLD.uid;
        DELETE FROM topic WHERE uid = OLD.uid;
        DELETE FROM group_user WHERE uid = OLD.uid;
        DELETE FROM "group" WHERE uid = OLD.uid;
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        IF (NEW.warnned_times >= 5) THEN
            UPDATE "user" SET is_forbid = true WHERE uid = OLD.uid;
        END IF;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;


--------------------------------------------------------------------------------
-- 触发器
--------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS article_before_t ON article;
CREATE TRIGGER article_before_t BEFORE DELETE OR UPDATE ON article
   FOR EACH ROW EXECUTE PROCEDURE article_before_t();

DROP TRIGGER IF EXISTS topic_before_t ON topic;
CREATE TRIGGER topic_before_t BEFORE DELETE ON topic
   FOR EACH ROW EXECUTE PROCEDURE topic_before_t();

DROP TRIGGER IF EXISTS topic_after_t ON topic;
CREATE TRIGGER topic_after_t AFTER INSERT ON topic
   FOR EACH ROW EXECUTE PROCEDURE topic_after_t();

DROP TRIGGER IF EXISTS group_chat_after_t ON group_chat;
CREATE TRIGGER group_chat_after_t AFTER INSERT ON group_chat
   FOR EACH ROW EXECUTE PROCEDURE group_chat_after_t();

DROP TRIGGER IF EXISTS group_before_t ON "group";
CREATE TRIGGER group_before_t BEFORE DELETE ON "group"
   FOR EACH ROW EXECUTE PROCEDURE group_before_t();

DROP TRIGGER IF EXISTS group_after_t ON "group";
CREATE TRIGGER group_after_t AFTER INSERT ON "group"
   FOR EACH ROW EXECUTE PROCEDURE group_after_t();

DROP TRIGGER IF EXISTS user_before_t ON "user";
CREATE TRIGGER user_before_t BEFORE DELETE OR UPDATE ON "user"
   FOR EACH ROW EXECUTE PROCEDURE user_before_t();
