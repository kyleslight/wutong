/*
 Host     : localhost
 Database : PostgreSQL
 Port     : 5432
 Encoding : utf-8
*/

SET client_min_messages = ERROR;
SET client_encoding = 'UTF8';
CREATE EXTENSION IF NOT EXISTS pgcrypto;


-------------------------------------------------------------------------------
-- sequence
-------------------------------------------------------------------------------

DROP SEQUENCE IF EXISTS message_seq CASCADE;
CREATE SEQUENCE message_seq;


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
    -- true == man
    sex bool,
    age smallint CHECK (age BETWEEN 1 AND 130 OR age IS NULL),
    -- 位置
    address varchar(1000),
    -- 简介
    intro varchar(2000),
    -- 签名
    motto varchar(1000),
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


-- 用户头衔
DROP TABLE IF EXISTS user_title CASCADE;
CREATE TABLE user_title (
    id serial PRIMARY KEY,
    uid int REFERENCES "user"(uid) NOT NULL,
    name varchar(20) NOT NULL,
    create_time timestamp NOT NULL DEFAULT now()
);


DROP TABLE IF EXISTS notification CASCADE;
CREATE TABLE notification (
    id serial PRIMARY KEY,
    -- 发送者
    uid int REFERENCES "user"(uid) NOT NULL,
    -- 接收者
    receiver varchar(32) REFERENCES "user"(penname),
    title varchar(500),
    content varchar(27262),
    type varchar(6) CHECK (type IN ('公告', '回复', '推送', '私信')),
    url varchar(255),
    is_viewed bool DEFAULT false,
    create_time timestamp NOT NULL DEFAULT now()
);


DROP TABLE IF EXISTS memo CASCADE;
CREATE TABLE memo (
    id serial PRIMARY KEY,
    uid int REFERENCES "user"(uid) NOT NULL,
    title varchar(500),
    content varchar(27262),
    create_time timestamp NOT NULL DEFAULT now()
);


DROP TABLE IF EXISTS article CASCADE;
CREATE TABLE article (
    aid serial PRIMARY KEY,
    -- 创建者
    uid int REFERENCES "user"(uid) NOT NULL,
    title varchar(500) NOT NULL,
    mainbody varchar(272629) NOT NULL,
    -- 描述
    description varchar(1000),
    -- 适合
    suit_for varchar(1000),
    -- 参考来源
    reference varchar(1000),
    -- 系列
    series varchar(500),
    -- 资源
    resource varchar(2550),
    submit_time timestamp NOT NULL DEFAULT now(),
    last_modify_time timestamp,
    -- 公开性 --> '不公开', '不推送', '推送'
    is_public int CHECK (is_public BETWEEN 0 AND 2) DEFAULT 2,
    is_deleted bool NOT NULL DEFAULT false
);


DROP TABLE IF EXISTS article_history CASCADE;
CREATE TABLE article_history (
    id serial PRIMARY KEY,
    aid int REFERENCES article(aid) NOT NULL,
    title varchar(500) NOT NULL,
    mainbody varchar(272629) NOT NULL,
    description varchar(1000),
    suit_for varchar(1000),
    reference varchar(1000),
    series varchar(500),
    resource varchar(255),
    modify_time timestamp NOT NULL DEFAULT now()
);


DROP TABLE IF EXISTS article_user CASCADE;
CREATE TABLE article_user (
    auid serial PRIMARY KEY,
    aid int REFERENCES article(aid) NOT NULL,
    uid int REFERENCES "user"(uid) NOT NULL,
    -- 用户对文章的评分
    score int CHECK (score BETWEEN 1 AND 10),
    -- 合作编辑
    is_coeditor bool NOT NULL DEFAULT false,
    -- 收藏
    is_collected bool NOT NULL DEFAULT false,
    -- 转发
    is_forwarded bool NOT NULL DEFAULT false,
    CHECK (is_coeditor OR is_collected OR is_forwarded),
    UNIQUE (aid, uid)
);


-- 文章评论
DROP TABLE IF EXISTS article_comment CASCADE;
CREATE TABLE article_comment (
    id serial PRIMARY KEY,
    aid int REFERENCES article(aid) NOT NULL,
    uid int REFERENCES "user"(uid) NOT NULL,
    content varchar(200) NOT NULL,
    -- 段落id
    paragraph_id varchar(50),
    -- 侧评
    is_side bool NOT NULL DEFAULT false,
    floor int DEFAULT 1,
    create_time timestamp NOT NULL DEFAULT now()
);


-- 文章读者群
DROP TABLE IF EXISTS article_appositeness CASCADE;
CREATE TABLE article_appositeness (
    id serial PRIMARY KEY,
    aid int REFERENCES article(aid) NOT NULL,
    name varchar(20) NOT NULL,
    create_time timestamp NOT NULL DEFAULT now()
);


-- 文章标签
DROP TABLE IF EXISTS article_tag CASCADE;
CREATE TABLE article_tag (
    id serial PRIMARY KEY,
    aid int REFERENCES article(aid) NOT NULL,
    name varchar(20) NOT NULL,
    create_time timestamp NOT NULL DEFAULT now()
);


-- 文章成就
DROP TABLE IF EXISTS article_honor CASCADE;
CREATE TABLE article_honor (
    id serial PRIMARY KEY,
    aid int REFERENCES article(aid) NOT NULL,
    name varchar(20) NOT NULL,
    create_time timestamp NOT NULL DEFAULT now()
);


-- 浏览过文章的用户
DROP TABLE IF EXISTS article_view CASCADE;
CREATE TABLE article_view (
    id serial PRIMARY KEY,
    aid int REFERENCES article(aid) NOT NULL,
    uid int REFERENCES "user"(uid),
    ip varchar(40),
    view_time timestamp NOT NULL DEFAULT now()
);


-- 收藏文章的用户
DROP TABLE IF EXISTS article_collection CASCADE;
CREATE TABLE article_collection (
    id serial PRIMARY KEY,
    aid int REFERENCES article(aid) NOT NULL,
    uid int REFERENCES "user"(uid) NOT NULL,
    create_time timestamp NOT NULL DEFAULT now(),
    UNIQUE (aid, uid)
);


-- 文章的评分
DROP TABLE IF EXISTS article_score CASCADE;
CREATE TABLE article_score (
    id serial PRIMARY KEY,
    aid int REFERENCES article(aid) NOT NULL,
    uid int REFERENCES "user"(uid) NOT NULL,
    score int CHECK (score BETWEEN 1 AND 10) NOT NULL,
    create_time timestamp NOT NULL DEFAULT now(),
    UNIQUE (aid, uid)
);


DROP TABLE IF EXISTS "group" CASCADE;
CREATE TABLE "group" (
    gid serial PRIMARY KEY,
    -- 创建者
    uid int REFERENCES "user"(uid) NOT NULL,
    name varchar(32) NOT NULL,
    intro varchar(200),
    motto varchar(100),
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
    gid int REFERENCES "group"(gid) NOT NULL,
    uid int REFERENCES "user"(uid) NOT NULL,
    -- 组长
    is_leader bool NOT NULL DEFAULT false,
    -- 副组长
    is_subleader bool NOT NULL DEFAULT false,
    -- 组员
    is_member bool NOT NULL DEFAULT true,
    join_time timestamp DEFAULT now(),
    UNIQUE (gid, uid)
);


-- 小组公告
DROP TABLE IF EXISTS group_bulletin CASCADE;
CREATE TABLE group_bulletin (
    id serial PRIMARY KEY,
    gid int REFERENCES "group"(gid) NOT NULL,
    uid int REFERENCES "user"(uid) NOT NULL,
    title varchar(5000) NOT NULL,
    content varchar(400000) NOT NULL,
    submit_time timestamp NOT NULL DEFAULT now()
);


-- 小组topic
DROP TABLE IF EXISTS topic CASCADE;
CREATE TABLE topic (
    tid int PRIMARY KEY DEFAULT nextval('message_seq'),
    gid int REFERENCES "group"(gid) NOT NULL,
    uid int REFERENCES "user"(uid) NOT NULL,
    content varchar(400000) NOT NULL,
    submit_time timestamp NOT NULL DEFAULT now(),
    reply_id int REFERENCES topic(tid),
    last_reply_time timestamp,
    reply_times int DEFAULT 0,
    title varchar(5000),
    level int CHECK (level BETWEEN 0 AND 3) DEFAULT 0
);


DROP TABLE IF EXISTS group_chat CASCADE;
CREATE TABLE group_chat (
    id int PRIMARY KEY DEFAULT nextval('message_seq'),
    gid int REFERENCES "group"(gid) NOT NULL,
    uid int REFERENCES "user"(uid) NOT NULL,
    content varchar(400000) NOT NULL,
    submit_time timestamp NOT NULL DEFAULT now(),
    reply_id int REFERENCES topic(tid)
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
SELECT a.*, u.avatar, u.penname AS author
  FROM article a,
       "user" u
 WHERE a.uid = u.uid;


CREATE OR REPLACE VIEW article_comment_v
  AS
SELECT c.*, u.avatar, u.penname
  FROM article_comment c,
       user_info_v u
 WHERE c.uid = u.uid;


CREATE OR REPLACE VIEW article_collection_v
  AS
SELECT ac.*,
       a.title, a.author, a.avatar
  FROM article_collection ac,
       article_info_v a
 WHERE ac.aid = a.aid;


CREATE OR REPLACE VIEW group_member_info_v
  AS
SELECT gu.*,
       u.penname, u.avatar,
       u.motto, u.intro,
       u.sex, u.age, u.address
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
       NULL AS "reply_times",
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
