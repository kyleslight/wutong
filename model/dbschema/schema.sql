-- PostgreSQL

SET client_min_messages = ERROR;
SET client_encoding = 'UTF8';
CREATE EXTENSION IF NOT EXISTS pgcrypto;


-------------------------------------------------------------------------------
-- table
-------------------------------------------------------------------------------

DROP TABLE IF EXISTS "user" CASCADE;
CREATE TABLE "user" (
    uid serial PRIMARY KEY,
    email varchar(50) UNIQUE NOT NULL,
    penname varchar(32) UNIQUE NOT NULL,
    phone varchar(18) UNIQUE,
    password varchar(128) NOT NULL,
    realname varchar(32),
    sex varchar(6) CHECK (sex IN ('男', '女', 'male', 'female', NULL)),
    age smallint CHECK (age BETWEEN 0 AND 130 OR age IS NULL),
    -- 位置
    address varchar(1000),
    -- 简介
    intro varchar(2000),
    -- 签名
    motton varchar(1000),
    -- 头像url
    avatar varchar(255),
    register_date timestamp NOT NULL DEFAULT now(),
    -- 被警告次数
    warnned_times int NOT NULL DEFAULT 0,
    -- 邮箱激活
    is_activated bool NOT NULL DEFAULT false,
    is_forbid bool NOT NULL DEFAULT false,
    is_deleted bool NOT NULL DEFAULT false,
    is_admin bool NOT NULL DEFAULT false
);


DROP TABLE IF EXISTS article CASCADE;
CREATE TABLE article (
    aid serial PRIMARY KEY,
    -- 创建者
    uid integer REFERENCES "user"(uid) NOT NULL,
    title varchar(500) NOT NULL,
    mainbody varchar(272629) NOT NULL,
    subtitle varchar(500),
    -- 描述
    desciption varchar(1000),
    -- 参考
    reference varchar(1000),
    -- 系列
    series varchar(500),
    -- 资源url
    resource varchar(255),
    submit_time timestamp NOT NULL DEFAULT now(),
    -- 公开性
    is_public bool NOT NULL DEFAULT true,
    is_deleted bool NOT NULL DEFAULT false
);


DROP TABLE IF EXISTS article_history CASCADE;
CREATE TABLE article_history (
    id serial PRIMARY KEY,
    aid integer REFERENCES article(aid) NOT NULL,
    title varchar(500) NOT NULL,
    mainbody varchar(272629) NOT NULL,
    subtitle varchar(500),
    desciption varchar(1000),
    reference varchar(1000),
    series varchar(500),
    resource varchar(255),
    modify_time timestamp NOT NULL DEFAULT now()
);


DROP TABLE IF EXISTS "group" CASCADE;
CREATE TABLE "group" (
    gid serial PRIMARY KEY,
    -- 创建者
    uid integer REFERENCES "user"(uid) NOT NULL,
    name varchar(32) NOT NULL,
    intro varchar(200),
    motton varchar(100),
    description varchar(500),
    foundtime timestamp NOT NULl DEFAULT now(),
    -- 头像url
    avatar varchar(255),
    -- 图片url
    banner varchar(255),
    -- 公开性
    is_public bool NOT NULL DEFAULT true,
    -- 成员数
    member_number int DEFAULT 1
);


DROP TABLE IF EXISTS group_user CASCADE;
CREATE TABLE group_user (
    guid serial PRIMARY KEY,
    gid integer REFERENCES "group"(gid) NOT NULL,
    uid integer REFERENCES "user"(uid) NOT NULL,
    -- 组长
    is_leader bool NOT NULL DEFAULT false,
    -- 副组长
    is_subleader bool NOT NULL DEFAULT false,
    -- 组员
    is_member bool NOT NULL DEFAULT true,
    join_time timestamp DEFAULT now(),
    UNIQUE (gid, uid)
);


DROP TABLE IF EXISTS article_user CASCADE;
CREATE TABLE article_user (
    auid serial PRIMARY KEY,
    aid integer REFERENCES article(aid) NOT NULL,
    uid integer REFERENCES "user"(uid) NOT NULL,
    -- 用户对文章的评分
    score int CHECK (score >= 0),
    -- 合作编辑
    is_coeditor bool NOT NULL DEFAULT false,
    -- 收藏
    is_collected bool NOT NULL DEFAULT false,
    -- 转发
    is_forwarded bool NOT NULL DEFAULT false,
    CHECK (is_coeditor OR is_collected OR is_forwarded),
    UNIQUE (aid, uid)
);


-- 小组topic
DROP TABLE IF EXISTS topic CASCADE;
DROP SEQUENCE IF EXISTS message_seq CASCADE;
CREATE SEQUENCE message_seq;
CREATE TABLE topic (
    tid integer PRIMARY KEY DEFAULT nextval('message_seq'),
    gid integer REFERENCES "group"(gid) NOT NULL,
    uid integer REFERENCES "user"(uid) NOT NULL,
    content varchar(400000) NOT NULL,
    reply_id integer REFERENCES topic(tid),
    submit_time timestamp NOT NULL DEFAULT now(),
    last_reply_time timestamp,
    title varchar(5000),
    level int CHECK (level BETWEEN 0 AND 3) DEFAULT 0
);


-- 用户头衔
DROP TABLE IF EXISTS user_title CASCADE;
CREATE TABLE user_title (
    id serial PRIMARY KEY,
    uid integer REFERENCES "user"(uid) NOT NULL,
    name varchar(20) NOT NULL,
    create_time timestamp NOT NULL DEFAULT now()
);


-- 文章评论
DROP TABLE IF EXISTS article_comment CASCADE;
CREATE TABLE article_comment (
    id serial PRIMARY KEY,
    aid integer REFERENCES article(aid) NOT NULL,
    uid integer REFERENCES "user"(uid) NOT NULL,
    content varchar(200) NOT NULL,
    -- 段落id
    paragraph_id varchar(50),
    -- 侧评
    is_side bool NOT NULL DEFAULT false,
    create_time timestamp NOT NULL DEFAULT now()
);


-- 文章读者群
DROP TABLE IF EXISTS article_appositeness CASCADE;
CREATE TABLE article_appositeness (
    id serial PRIMARY KEY,
    aid integer REFERENCES article(aid) NOT NULL,
    name varchar(20) NOT NULL,
    create_time timestamp NOT NULL DEFAULT now()
);


-- 文章标签
DROP TABLE IF EXISTS article_tag CASCADE;
CREATE TABLE article_tag (
    id serial PRIMARY KEY,
    aid integer REFERENCES article(aid) NOT NULL,
    name varchar(20) NOT NULL,
    create_time timestamp NOT NULL DEFAULT now()
);


-- 文章成就
DROP TABLE IF EXISTS article_honor CASCADE;
CREATE TABLE article_honor (
    id serial PRIMARY KEY,
    aid integer REFERENCES article(aid) NOT NULL,
    name varchar(20) NOT NULL,
    create_time timestamp NOT NULL DEFAULT now()
);


-- 浏览过文章的用户
DROP TABLE IF EXISTS article_view CASCADE;
CREATE TABLE article_view (
    id serial PRIMARY KEY,
    aid integer REFERENCES article(aid) NOT NULL,
    uid integer REFERENCES "user"(uid) NOT NULL,
    view_time timestamp NOT NULL DEFAULT now()
);


-- 小组公告
DROP TABLE IF EXISTS group_bulletin CASCADE;
CREATE TABLE group_bulletin (
    id serial PRIMARY KEY,
    gid integer REFERENCES "group"(gid) NOT NULL,
    uid integer REFERENCES "user"(uid) NOT NULL,
    title varchar(5000) NOT NULL,
    content varchar(400000) NOT NULL,
    submit_time timestamp NOT NULL DEFAULT now()
);


DROP TABLE IF EXISTS group_chat CASCADE;
CREATE TABLE group_chat (
    id integer PRIMARY KEY DEFAULT nextval('message_seq'),
    gid integer REFERENCES "group"(gid) NOT NULL,
    uid integer REFERENCES "user"(uid) NOT NULL,
    content varchar(400000) NOT NULL,
    reply_id integer REFERENCES topic(tid),
    submit_time timestamp NOT NULL DEFAULT now()
);


--------------------------------------------------------------------------------
-- view
--------------------------------------------------------------------------------

CREATE OR REPLACE VIEW user_info_v
  AS
SELECT u.*
  FROM "user" u;


CREATE OR REPLACE VIEW article_info_v
  AS
SELECT a.*, u.penname AS author
  FROM article a,
       "user" u
 WHERE a.uid = u.uid;


CREATE OR REPLACE VIEW group_member_info_v
  AS
SELECT gu.*, u.penname, u.avatar, u.motton
  FROM group_user gu,
       user_info_v u
 WHERE gu.is_member
   AND gu.uid = u.uid;


CREATE OR REPLACE VIEW group_info_v
  AS
SELECT g.*,
       u.penname AS founder,
       gm.penname AS leader
  FROM "group" g,
       "user" u,
       group_member_info_v gm
 WHERE g.uid = u.uid
   AND g.gid = gm.gid
   AND gm.is_leader;


CREATE OR REPLACE VIEW group_topic_v
  AS
SELECT u.penname, u.avatar, t.*
  FROM topic t,
       user_info_v u
 WHERE t.uid = u.uid;


CREATE OR REPLACE VIEW group_chat_v
  AS
SELECT u.penname, u.avatar, gc.*
  FROM group_chat gc,
       user_info_v u
 WHERE gc.uid = u.uid;


CREATE OR REPLACE VIEW group_message_v
  AS
SELECT *,
       submit_time AS "last_reply_time",
       NULL AS "title",
       NULL AS "level"
  FROM group_chat_v gc
 UNION
SELECT *
  FROM group_topic_v gt;


CREATE OR REPLACE VIEW group_bulletin_v
  AS
SELECT gb.*, u.penname, u.avatar
  FROM group_bulletin gb,
       user_info_v u
 WHERE gb.uid = u.uid;


--------------------------------------------------------------------------------
-- function
--------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION get_uid(account_s varchar)
  RETURNS integer
AS $$
    SELECT uid
      FROM "user"
     WHERE email = $1
        OR penname = $1
        OR phone = $1;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_user_permission(uid_i integer)
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


CREATE OR REPLACE FUNCTION get_user_info(uid_i integer)
  RETURNS json
AS $$
    SELECT row_to_json(j.*)
      FROM (
            SELECT *
              FROM user_info_v
             WHERE uid = $1
        ) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION do_register_user(
    email_s varchar,
    penname_s varchar,
    password_s varchar)
  RETURNS varchar AS
$$
DECLARE
    hashuid_s varchar;
BEGIN
    PERFORM uid
       FROM "user"
      WHERE email = $1
         OR penname = $2;
    IF FOUND THEN
        RETURN NULL;
    END IF;

    INSERT INTO "user" (
        email, penname, password)
    VALUES (
        $1, $2, crypt($3, gen_salt('bf')))
    RETURNING md5(CAST(uid AS varchar))
    INTO hashuid_s;
    RETURN hashuid_s;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION do_activate_user(hashuid_s varchar)
  RETURNS integer AS
$$
    UPDATE "user"
       SET is_activated = true
     WHERE is_activated = false
       AND $1 = md5(CAST(uid AS varchar))
     RETURNING uid;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION do_login_user(
    account_s varchar,
    password_s varchar)
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


CREATE OR REPLACE FUNCTION get_group_permission(
    gid_i integer,
    uid_i integer)
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
    motton varchar DEFAULT NULL,
    avatar varchar DEFAULT NULL,
    banner varchar DEFAULT NULL,
    is_public bool DEFAULT true)
  RETURNS integer
AS $$
    INSERT INTO "group" (
        uid, name, intro, motton,
        avatar, banner, is_public)
    VALUES (
        uid, name, intro, motton,
        avatar, banner, is_public)
    RETURNING gid;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION join_group(
    gid_i integer,
    uid_i integer)
  RETURNS integer
AS $$
    INSERT INTO group_user (gid, uid) VALUES ($1, $2)
    RETURNING guid;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_group_member_info(
    gid_i integer,
    uid_i integer)
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


CREATE OR REPLACE FUNCTION get_group_chats(
    gid_i integer,
    limit_i integer,
    offset_i integer)
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
    id_i integer)
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
    gid_i integer,
    uid_i integer,
    title_s varchar,
    content_s varchar,
    reply_id_i integer)
  RETURNS integer
AS $$
    INSERT INTO topic (
        gid, uid, title, content, reply_id)
    VALUES ($1, $2, $3, $4, $5)
    RETURNING tid;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_topics(
    gid_i integer,
    limit_i integer,
    offset_i integer)
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


CREATE OR REPLACE FUNCTION get_topic(tid_i integer)
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
    reply_id_i integer,
    limit_i integer,
    offset_i integer)
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
    reply_id_i integer,
    limit_i integer,
    offset_i integer)
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
    gid_i integer,
    uid_i integer,
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
    topic_id_i integer,
    limit_i integer,
    offset_i integer)
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


CREATE OR REPLACE FUNCTION get_group_message(msg_id_i integer)
  RETURNS json
AS $$
    SELECT row_to_json(j.*)
      FROM (
            SELECT *
              FROM group_message_v
             WHERE id = $1) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_group_messages(
    group_id_i integer,
    limit_i integer,
    offset_i integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(j))
      FROM (
            SELECT *
              FROM group_message_v
             WHERE gid = $1
             ORDER BY last_reply_time DESC
             LIMIT $2
            OFFSET $3) j;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_topic_messages(
    topic_id_i integer,
    limit_i integer,
    offset_i integer)
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
    gid_i integer,
    limit_i integer,
    offset_i integer)
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
    gid_i integer,
    uid_i integer,
    title_s varchar,
    content_s varchar)
  RETURNS integer
AS $$
    INSERT INTO group_bulletin (
        gid, uid, title, content)
    VALUES ($1, $2, $3, $4)
    RETURNING id;
$$ LANGUAGE SQL;


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
            aid, title, mainbody, subtitle,
            desciption, reference, series, resource)
        SELECT aid, title,
               mainbody, subtitle,
               desciption, reference,
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
        UPDATE topic SET last_reply_time = now() WHERE tid = NEW.tid;
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
        UPDATE topic SET last_reply_time = now() WHERE tid = NEW.reply_id;
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
