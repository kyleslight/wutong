-- host     : localhost
-- database : postgresql
-- port     : 5432
-- encoding : utf-8

-------------------------------------------------------------------------------
-- setting
-------------------------------------------------------------------------------
set client_min_messages = error;
set client_encoding = 'utf8';
create extension if not exists pgcrypto;

-------------------------------------------------------------------------------
-- domain
-------------------------------------------------------------------------------
drop domain if exists email cascade;
create domain email as text;

drop domain if exists url cascade;
create domain url as text;

drop domain if exists sort cascade;
create domain sort as char(1);

-------------------------------------------------------------------------------
-- table
-------------------------------------------------------------------------------

-- `user`是`postgresql`的关键字, 所以换个名
drop table if exists myuser cascade;
create table myuser (
    uid serial primary key,
    nickname text unique,
    email email unique,
    password text,
    avatar url,
    realname text,
    phone text,
    sex bool,
    birthday date,
    address text,
    -- 简介
    intro text,
    -- 签名
    motto text,
    register_ip inet,
    register_time timestamp default now(),
    -- 被警告次数
    warned_num smallint default 0,
    -- 邮箱激活
    is_activated bool default false,
    is_forbid bool default false,
    is_deleted bool default false,
    type sort default '1'
);


-- NOTICE: 所有 `base_` 开头的table均不用于存放数据, 仅仅被子表继承或查询用
-- 定义父表的注意事项:
-- 1.不要定义primary key
-- 2.不要使用serial类型
drop table if exists base_setting cascade;
create table base_setting (
    -- relate_id int,
    content json,
    modify_time timestamp default now()
);

drop table if exists user_setting cascade;
create table user_setting (
    id serial primary key,
    uid int
) inherits (base_setting);


drop table if exists user_ip cascade;
create table user_ip (
    id serial primary key,
    uid int,
    login_ip inet,
    login_time timestamp default now()
);


drop table if exists user_honor cascade;
create table user_honor (
    id serial primary key,
    uid int,
    name text,
    -- 1: title, 2: honor
    type sort,
    time timestamp default now()
);


drop table if exists user_message cascade;
create table user_message (
    id serial primary key,
    uid int,
    -- 字典, 存储键值对
    content json,
    type sort,
    is_viewed bool default false,
    time timestamp default now()
);


drop table if exists user_collection cascade;
create table user_collection (
    id serial primary key,
    uid int,
    relevant_id int,
    -- 1: article,  2: group topic
    type sort,
    create_time timestamp default now()
);


drop table if exists base_session cascade;
create table base_session (
    anchor_id serial,
    uid int,
    content text,
    reply_time timestamp default now(),
    create_time timestamp default now()
);

drop table if exists user_whisper cascade;
create table user_whisper (
    id serial primary key,
    another_uid int
) inherits (base_session);

drop table if exists user_memo cascade;
create table user_memo (
    id serial primary key,
    uid int,
    title text,
    content text,
    modify_time timestamp default now(),
    create_time timestamp default now()
);


drop table if exists user_relationship cascade;
create table user_relationship (
    id serial primary key,
    uid int,
    another_uid int,
    -- 1: block   2: star   3: friend
    relate_level sort,
    time timestamp default now()
);


drop table if exists base_opus cascade;
create table base_opus (
    uid int,
    title text,
    mainbody text,
    -- 引言
    intro text,
    -- 适合
    suit_for text,
    -- 参考来源
    refers text[],
    -- 系列
    series text,
    -- 资源
    resources text[],
    create_time timestamp default now(),
    -- 1=草稿, 2=私有, 3=公开不推送, 4=公开并推送
    public_level sort default '4'
);

drop table if exists article cascade;
create table article (
    aid serial primary key,
    modify_time timestamp default now(),
    is_deleted bool default false
) inherits (base_opus);

drop table if exists article_backup cascade;
create table article_backup (
    id serial primary key
) inherits (base_opus);


drop table if exists article_setting cascade;
create table article_setting (
    id serial primary key,
    aid int
) inherits (base_setting);


drop table if exists base_tag cascade;
create table base_tag (
    -- relate_id int,
    content text
);

drop table if exists article_tag cascade;
create table article_tag (
    id serial primary key,
    aid int
) inherits (base_tag);


drop table if exists article_honor cascade;
create table article_honor (
    id serial primary key,
    aid int,
    content text,
    type sort,
    time timestamp default now()
);


drop table if exists article_coeditor cascade;
create table article_coeditor (
    id serial primary key,
    aid int,
    nickname text
);


drop table if exists base_article_user cascade;
create table base_article_user (
    aid int,
    uid int
);

drop table if exists article_view cascade;
create table article_view (
    id serial primary key,
    ip inet,
    time timestamp default now()
) inherits (base_article_user);


drop table if exists article_score cascade;
create table article_score (
    id serial primary key,
    score smallint,
    time timestamp default now()
) inherits (base_article_user);

drop table if exists article_forwarded cascade;
create table article_forwarded (
    id serial primary key,
    ip inet,
    time timestamp default now()
) inherits (base_article_user);


drop table if exists base_article_comment cascade;
create table base_article_comment (
    aid int,
    uid int,
    content text,
    modify_time timestamp default now(),
    create_time timestamp default now()
);

drop table if exists article_bottom_comment cascade;
create table article_bottom_comment (
    id serial primary key,
    reply_id int,
    rank int
) inherits (base_article_comment);

drop table if exists article_side_comment cascade;
create table article_side_comment (
    id serial primary key,
    -- 段落id
    paragraph_id text
) inherits (base_article_comment);


-- `group`是`postgresql`的关键字, 所以换个名
drop table if exists mygroup cascade;
create table mygroup (
    gid serial primary key,
    -- 创建者
    uid int,
    name text,
    avatar url,
    intro text,
    motto text,
    -- 图片
    banner url,
    -- 1=非公开, 2=公开
    public_level sort default '2',
    create_time timestamp default now()
);


drop table if exists group_setting cascade;
create table group_setting (
    id serial primary key,
    gid int
) inherits (base_setting);


drop table if exists group_tag cascade;
create table group_tag (
    id serial primary key,
    gid int
) inherits (base_tag);


drop table if exists base_group_user cascade;
create table base_group_user (
    gid int,
    uid int
);

drop table if exists group_member cascade;
create table group_member (
    id serial primary key,
    -- 1=申请加入, 2=成员, 3=副组长, 4=组长
    position_level sort,
    join_time timestamp default now()
) inherits (base_group_user);


drop table if exists group_member_setting cascade;
create table group_member_setting (
    id serial primary key,
    gid int,
    uid int
) inherits (base_setting);


drop table if exists group_topic cascade;
create table group_topic (
    tid serial primary key,
    gid int,
    title text,
    father_id int,
    ancestor_id int,
    on_top bool default false
) inherits (base_session);

drop table if exists group_message cascade;
create table group_message (
    id serial primary key,
    gid int,
    tid int,
    on_top bool default false
) inherits (base_session);

--------------------------------------------------------------------------------
-- view
--------------------------------------------------------------------------------

-- 所有后缀为`_base`的view都不应该直接通过`psycopg2`调用
-- 而只用做支撑其它sql语句
drop view if exists user_base cascade;
create view user_base
  as
select uid,
       nickname,
       avatar
  from myuser;

drop view if exists user_show cascade;
create view user_show
  as
select u.*
  from myuser u;

drop view if exists article_tag_base cascade;
create view article_tag_base
  as
select aid,
       array_agg(content) as "tags"
  from article_tag
 group by aid;

drop view if exists article_coeditor_base cascade;
create view article_coeditor_base
  as
select aid,
       array_agg(nickname) as "coeditors"
  from article_coeditor
 group by aid;

drop view if exists article_base cascade;
create view article_base
  as
select a.uid,
       a.aid,
       a.title,
       a.intro,
       a.modify_time,
       a.public_level,
       a.is_deleted,
       at.tags,
       u.nickname as "author",
       u.avatar as "author_avatar"
  from article a,
       article_tag_base at,
       user_base u
 where a.uid = u.uid
   and a.aid = at.aid;

drop view if exists article_collection cascade;
create view article_collection
  as
select *,
       relevant_id as "aid"
  from user_collection
 where type = '1';

drop view if exists article_interact_info cascade;
create view article_interact_info
  as
select a.aid,
       COALESCE((select count(id) from article_view where a.aid = aid), 0) as "view_num",
       COALESCE((select avg(score) from article_score where a.aid = aid), 0) as "avg_score",
       COALESCE((select count(id) from user_collection where a.aid = relevant_id and type = '1'), 0) as "collected_num",
       COALESCE((select count(id) from article_forwarded where a.aid = aid), 0) as "forwarded_num"
  from article a;

-- 所有后缀为`_show`的view都含有渲染所需要的全部数据
-- 也可能会包含有不应该被客户端知晓的数据, 因此不应该被直接传给客户端
drop view if exists article_show cascade;
create view article_show
  as
select a.*,
       at.tags,
       u.nickname as "author",
       u.avatar as "author_avatar"
  from article a,
       article_tag_base at,
       user_base u
 where a.uid = u.uid
   and a.aid = at.aid;

drop view if exists article_bottom_comment_show cascade;
create view article_bottom_comment_show
  as
select c.*,
       u.nickname as "creater",
       u.avatar as "creater_avatar"
  from article_bottom_comment c,
       user_base u
 where c.uid = u.uid;

drop view if exists article_side_comment_show cascade;
create view article_side_comment_show
  as
select c.*,
       u.nickname as "creater",
       u.avatar as "creater_avatar"
  from article_side_comment c,
       user_base u
 where c.uid = u.uid;

drop view if exists group_tag_base cascade;
create view group_tag_base
  as
select gid,
       array_agg(content) as "tags"
  from group_tag
 group by gid;

drop view if exists group_base cascade;
create view group_base
  as
select g.gid,
       g.name,
       g.avatar,
       gt.tags
  from mygroup g,
       group_tag_base gt
 where g.gid = gt.gid;

drop view if exists group_member_show cascade;
create view group_member_show
  as
select gm.*,
       u.nickname,
       u.avatar,
       u.intro,
       u.sex,
       u.birthday,
       u.address
  from group_member gm,
       myuser u
 where gm.uid = u.uid;

drop view if exists group_show cascade;
create view group_show
  as
select g.*,
       gt.tags,
       u.nickname as "creater",
       u.avatar as "creater_avatar",
       gm.nickname as "leader",
       gm.avatar as "leader_avatar",
       (select count(id) from group_member_show where gid = g.gid) as "member_number"
  from mygroup g,
       user_base u,
       group_member_show gm,
       group_tag_base gt
 where g.uid = u.uid
   and g.gid = gm.gid
   and g.gid = gt.gid
   and gm.position_level = '4';

drop view if exists group_topic_base cascade;
create view group_topic_base
  as
select t.*,
       u.nickname as "creater",
       u.avatar as "creater_avatar",
       (select count(id) from group_message where tid = t.tid) +
       (select count(tid) from group_topic where father_id = t.tid) as "reply_number"
  from group_topic t,
       user_base u
 where t.uid = u.uid;

drop view if exists group_topic_show cascade;
create view group_topic_show
  as
select t.*,
       (select row_to_json(j.*) from (select tid, title from group_topic where tid = t.father_id) j) as "father",
       (select row_to_json(j.*) from (select tid, title from group_topic where tid = t.ancestor_id) j) as "ancestor"
  from group_topic_base t,
       user_base u
 where t.uid = u.uid;

drop view if exists group_message_show cascade;
create view group_message_show
  as
select m.*,
       u.nickname as "creater",
       u.avatar as "creater_avatar"
  from group_message m,
       user_base u
 where m.uid = u.uid;

drop view if exists group_topic_collection cascade;
create view group_topic_collection
  as
select *,
       relevant_id as "tid"
  from user_collection
 where type = '2';

drop view if exists user_collected_article_show cascade;
create view user_collected_article_show
  as
select a.*,
       c.create_time as "collect_time"
  from article_collection c,
       article_base a,
       myuser u
 where c.uid = u.uid
   and c.aid = a.aid;

drop view if exists user_collected_topic_show cascade;
create view user_collected_topic_show
  as
select t.*,
       c.create_time as "collect_time"
  from group_topic_collection c,
       group_topic_base t,
       myuser u
 where c.uid = u.uid
   and c.tid = t.tid;


drop view if exists article_search cascade;
create view article_search
  as
select aid,
       title,
       intro,
       mainbody,
       modify_time,
       tags,
       author,
       author_avatar
  from article_show
 where public_level > '2'
   and not is_deleted;

drop view if exists group_search cascade;
create view group_search
  as
select gid,
       name,
       intro,
       motto,
       create_time,
       tags,
       creater,
       avatar
  from group_show
 where public_level > '1';

drop view if exists user_search cascade;
create view user_search
  as
select *
  from user_show;
