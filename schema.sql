-- 只显示错误信息
SET client_min_messages TO ERROR;

-- 用户权限信息
DROP TABLE IF EXISTS "user" CASCADE;
CREATE TABLE "user" (
    uid serial PRIMARY KEY,
    email varchar(50) UNIQUE NOT NULL,
    -- 用户名/昵称
    penname varchar(32) UNIQUE NOT NULL,
    phone varchar(18) UNIQUE,
    password varchar(128) NOT NULL,
    -- 验证状态
    status bool NOT NULL DEFAULT false,
    is_admin bool NOT NULL DEFAULT false
);

-- 用户详细信息
DROP TABLE IF EXISTS "user_info" CASCADE;
CREATE TABLE "user_info" (
    uiid serial PRIMARY KEY,
    uid serial REFERENCES "user"(uid),
    realname varchar(32),
    -- 男true 女false
    sex bool,
    age smallint,
    -- 位置
    address varchar(100),
    -- 简介
    intro varchar(200),
    -- 签名
    motton varchar(100),
    -- 头像url
    avatar varchar(255),
    register_date timestamp NOT NULL DEFAULT now(),
    -- 被警告次数
    warnned_times int NOT NULL DEFAULT 0
);

DROP TABLE IF EXISTS "article" CASCADE;
CREATE TABLE "article" (
    aid serial PRIMARY KEY,
    title varchar(50) NOT NULL,
    mainbody varchar(272629) NOT NULL,
    -- 副标题
    subhead varchar(50),
    -- 描述
    desciption varchar(100),
    -- 参考
    reference varchar(100),
    -- 系列
    series varchar(50),
    -- 小品
    is_fragment bool NOT NULL DEFAULT false,
    -- 资源url
    resource varchar(255),
    -- 公开性
    publicity bool NOT NULL DEFAULT true,
    submit_time timestamp NOT NULL DEFAULT now()
);

-- 小组
DROP TABLE IF EXISTS "group" CASCADE;
CREATE TABLE "group" (
    gid serial PRIMARY KEY,
    name varchar(32),
    foundtime timestamp NOT NULl DEFAULT now(),
    score int NOT NULL DEFAULT 0,
    intro varchar(200),
    motton varchar(100),
    -- 公告
    bulletin varchar(200),
    -- 创建者penname
    founder varchar(200),
    -- 公开性
    publicity bool NOT NULL DEFAULT true
);

-- 用户头衔
DROP TABLE IF EXISTS "user_title" CASCADE;
CREATE TABLE "user_title" (
    utid serial PRIMARY KEY,
    uid serial REFERENCES "user"(uid),
    name varchar(20),
    create_time timestamp NOT NULL DEFAULT now()
);

-- 文章-用户
DROP TABLE IF EXISTS "article_user" CASCADE;
CREATE TABLE "article_user" (
    auid serial PRIMARY KEY,
    aid serial REFERENCES "article"(aid),
    uid serial REFERENCES "user"(uid),
    -- 用户对文章的评分
    score int,
    is_author bool NOT NULL DEFAULT true,
    -- 合作编辑
    is_coeditor bool NOT NULL DEFAULT false,
    -- 收藏
    is_collected bool NOT NULL DEFAULT false,
    -- 转发
    is_forwarded bool NOT NULL DEFAULT false
);

-- 文章评论
DROP TABLE IF EXISTS "article_comment" CASCADE;
CREATE TABLE "article_comment" (
    acid serial PRIMARY KEY,
    aid serial REFERENCES "article"(aid),
    uid serial REFERENCES "user"(uid),
    content varchar(200) NOT NULL,
    -- 侧评
    is_side bool NOT NULL,
    -- 段落id
    paragraph_id varchar(50),
    create_time timestamp NOT NULL DEFAULT now()
);


-- 文章读者群, 类似tag
DROP TABLE IF EXISTS "article_appositeness" CASCADE;
CREATE TABLE "article_appositeness" (
    aaid serial PRIMARY KEY,
    aid serial REFERENCES "article"(aid),
    name varchar(20),
    create_time timestamp NOT NULL DEFAULT now()
);

-- 文章tag
DROP TABLE IF EXISTS "article_tag" CASCADE;
CREATE TABLE "article_tag" (
    atid serial PRIMARY KEY,
    aid serial REFERENCES "article"(aid),
    name varchar(20),
    create_time timestamp NOT NULL DEFAULT now()
);

-- 文章成就
DROP TABLE IF EXISTS "article_honor" CASCADE;
CREATE TABLE "article_honor" (
    ahid serial PRIMARY KEY,
    aid serial REFERENCES "article"(aid),
    name varchar(20),
    create_time timestamp NOT NULL DEFAULT now()
);

-- 浏览过文章的user
DROP TABLE IF EXISTS "article_view" CASCADE;
CREATE TABLE "article_view" (
    avid serial PRIMARY KEY,
    aid serial REFERENCES "article"(aid),
    uid serial REFERENCES "user"(uid),
    view_time timestamp NOT NULL DEFAULT now()
);

-- 浏览过小组的user
DROP TABLE IF EXISTS "group_user" CASCADE;
CREATE TABLE "group_user" (
    guid serial PRIMARY KEY,
    gid serial REFERENCES "group"(gid),
    uid serial REFERENCES "user"(uid),
    -- 组长
    is_leader bool NOT NULL DEFAULT false,
    -- 副组长
    is_subleader bool NOT NULL DEFAULT false,
    -- 组员
    is_member bool NOT NULL DEFAULT true,
    view_time timestamp NOT NULL DEFAULT now()
);

-- 小组消息
DROP TABLE IF EXISTS "group_chat" CASCADE;
CREATE TABLE "group_chat" (
    gcid serial PRIMARY KEY,
    -- 所回复的topic id
    gtid serial REFERENCES "group_topic"(gtid),
    uid serial REFERENCES "user"(uid),
    content varchar(400) NOT NULL,
    submit_time timestamp NOT NULL DEFAULT now()
);

-- 小组话题
DROP TABLE IF EXISTS "group_topic" CASCADE;
CREATE TABLE "group_topic" (
    gtid serial PRIMARY KEY,
    gid serial REFERENCES "group"(gid),
    uid serial REFERENCES "user"(uid),
    content varchar(400) NOT NULL,
    title varchar(50) NOT NULL,
    submit_time timestamp NOT NULL DEFAULT now()
);

-- 用户详细信息
DROP VIEW IF EXISTS v_user_info CASCADE;
CREATE VIEW v_user_info
  AS
SELECT email, penname, phone, 
       intro, motton, avatar, 
       realname, sex, age,
       address, register_date, 
       warnned_times, uid
  FROM "user" 
  NATURAL JOIN "user_info";

-- 用户得分
DROP VIEW IF EXISTS v_user_grade CASCADE;
CREATE VIEW v_user_grade
  AS
SELECT 0 AS "uid";

-- 小组消息
DROP VIEW IF EXISTS v_group_chats CASCADE;
CREATE VIEW v_group_chats
  AS
SELECT penname, content,
       submit_time
  FROM "user"
  NATURAL JOIN "group_chat";
