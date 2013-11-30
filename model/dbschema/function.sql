--------------------------------------------------------------------------------
-- 函数
--------------------------------------------------------------------------------

-- 用户详细信息
DROP FUNCTION IF EXISTS get_user_info_j(integer);
CREATE FUNCTION get_user_info_j(integer)
  RETURNS json
AS $$
    SELECT row_to_json(u.*)
      FROM (
           SELECT email, penname, phone,
                  intro, motton, avatar,
                  realname, sex, age,
                  address, register_date,
                  warnned_times, uid
             FROM "user"
             NATURAL JOIN "user_info"
             WHERE uid = $1
        ) u;
$$ LANGUAGE SQL;

-- 用户注册, return md5(uid)
DROP FUNCTION IF EXISTS register_user(varchar, varchar, varchar);
CREATE FUNCTION register_user(varchar, varchar, varchar)
  RETURNS varchar AS
$$
DECLARE
    v_email ALIAS FOR $1;
    v_penname ALIAS FOR $2;
    v_password ALIAS FOR $3;
    v_uid "user".uid%TYPE;
BEGIN
    -- 用户已存在?
    PERFORM "uid"
       FROM "user"
       WHERE "email" = v_email OR "penname" = v_penname;
    IF FOUND THEN
        RETURN NULL;
    END IF;
    -- 添加用户信息
    INSERT INTO "user"
           ("email", "password", "penname")
    VALUES (v_email, crypt(v_password, gen_salt('bf')), v_penname)
        RETURNING "uid" INTO v_uid;
    INSERT INTO "user_info" ("uid") VALUES (v_uid);
    -- 返回md5(uid)
    RETURN md5(CAST(v_uid AS varchar));
END;
$$ LANGUAGE plpgsql;

-- 激活用户, return uid
DROP FUNCTION IF EXISTS activate_user(varchar);
CREATE FUNCTION activate_user(varchar)
  RETURNS integer AS
$$
    UPDATE "user"
       SET ("is_activated") = (true)
     WHERE md5(CAST("uid" AS varchar)) = $1
    RETURNING "uid";
$$ LANGUAGE SQL;

-- 用户登录, return uid
DROP FUNCTION IF EXISTS user_login(varchar, varchar);
CREATE FUNCTION user_login(varchar, varchar)
  RETURNS integer AS $$
DECLARE
    v_account ALIAS FOR $1;
    v_password ALIAS FOR $2;
    v_uid "user".uid%TYPE;
BEGIN
    SELECT "uid" INTO v_uid
      FROM "user"
     WHERE "is_activated" = true
       AND ("email" = v_account
            OR "penname" = v_account
            OR "phone" = v_account)
       AND "password" = crypt(v_password, "password");
    RETURN v_uid;
END;
$$ LANGUAGE plpgsql;

-- 根据email或penname或phone返回uid
DROP FUNCTION IF EXISTS get_uid(varchar);
CREATE FUNCTION get_uid(varchar)
  RETURNS integer AS $$
DECLARE
    v_account ALIAS FOR $1;
    v_uid "user".uid%TYPE;
BEGIN
    SELECT "uid" INTO v_uid
      FROM "user"
     WHERE "email" = $1
        OR "penname" = $1
        OR "phone" = $1;
    RETURN v_uid;
END;
$$ LANGUAGE plpgsql;

--------------------------------------------------------------------------------
-- 小组详细信息
DROP FUNCTION IF EXISTS get_group_info_j(integer);
CREATE FUNCTION get_group_info_j(integer)
  RETURNS json
AS $$
    SELECT row_to_json(g.*)
      FROM (
           SELECT gid, name, founder,
                  intro, motton, publicity,
                  foundtime
             FROM "group"
             WHERE gid = $1
        ) g;
$$ LANGUAGE SQL;

-- 创建小组, return gid
DROP FUNCTION IF EXISTS create_group(varchar, varchar, varchar, varchar);
CREATE FUNCTION create_group(varchar, varchar, varchar, varchar)
  RETURNS integer
AS $$
    INSERT INTO "group"
           ("name", "founder", "intro", "motton")
    VALUES ($1, $2, $3, $4)
    RETURNING gid;
$$ LANGUAGE SQL;

-- 加入小组
DROP FUNCTION IF EXISTS join_group(integer, integer);
CREATE FUNCTION join_group(integer, integer)
  RETURNS void
AS $$
    INSERT INTO "group_user"
           ("gid", "uid")
    VALUES ($1, $2);
$$ LANGUAGE SQL;
--------------------------------------------------------------------------------
DROP FUNCTION IF EXISTS get_member_info_j(integer, integer);
CREATE FUNCTION get_member_info_j(integer, integer)
  RETURNS json
AS $$
    SELECT row_to_json(m.*)
      FROM (SELECT is_leader, is_subleader,
                   is_member, join_time
              FROM "group_user"
             WHERE gid = $1
               AND uid = $2) m;
$$ LANGUAGE SQL;

DROP FUNCTION IF EXISTS get_group_message_j(integer);
CREATE FUNCTION get_group_message_j(integer)
  RETURNS json
AS $$
    SELECT row_to_json(m.*)
      FROM (SELECT id, gid, uid,
                   content, reply_id,
                   submit_time
              FROM "group_message"
             WHERE id = $1) m;
$$ LANGUAGE SQL;

DROP FUNCTION IF EXISTS get_group_messages_j(integer, integer, integer);
CREATE FUNCTION get_group_messages_j(integer, integer, integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(gm))
      FROM (SELECT id, gid, uid,
                   content, reply_id,
                   submit_time
              FROM "group_message"
             WHERE gid = $1
             ORDER BY id DESC
             LIMIT $2
            OFFSET $3) gm;
$$ LANGUAGE SQL;

-------------------------------------------------------------------------------
DROP FUNCTION IF EXISTS insert_group_topic(integer, integer, varchar, varchar, integer);
CREATE FUNCTION insert_group_topic(integer, integer, varchar, varchar, integer)
  RETURNS integer
AS $$
    INSERT INTO "group_topic"
           (gid, uid, content, title, reply_id)
    VALUES ($1, $2, $3, $4, $5)
    RETURNING id;
$$ LANGUAGE SQL;

DROP FUNCTION IF EXISTS get_group_topic_j(integer);
CREATE FUNCTION get_group_topic_j(integer)
  RETURNS json
AS $$
    SELECT row_to_json(m.*)
      FROM (SELECT id, gid, uid,
                   content, title,
                   reply_id, submit_time
              FROM "group_topic"
             WHERE id = $1) m;
$$ LANGUAGE SQL;

DROP FUNCTION IF EXISTS get_group_topics_j(integer, integer, integer);
CREATE FUNCTION get_group_topics_j(integer, integer, integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(gt))
      FROM (SELECT id, gid, uid,
                   content, title, reply_id,
                   submit_time
              FROM "group_topic"
             WHERE gid = $1
               AND title IS NOT NULL
             ORDER BY id DESC
             LIMIT $2
            OFFSET $3) gt;
$$ LANGUAGE SQL;

DROP FUNCTION IF EXISTS get_topic_messages_j(integer, integer, integer);
CREATE FUNCTION get_topic_messages_j(integer, integer, integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(gm))
      FROM (SELECT id, gid, uid,
                   content, submit_time
              FROM "group_message"
             WHERE reply_id = $1
             ORDER BY id DESC
             LIMIT $2
            OFFSET $3) gm;
$$ LANGUAGE SQL;

DROP FUNCTION IF EXISTS insert_group_message(integer, integer, varchar, integer);
CREATE FUNCTION insert_group_message(integer, integer, varchar, integer)
  RETURNS integer
AS $$
    INSERT INTO "group_message"
           (gid, uid, content, reply_id)
    VALUES ($1, $2, $3, $4)
    RETURNING id;
$$ LANGUAGE SQL;

DROP FUNCTION IF EXISTS group_bulletins_j(integer, integer, integer);
CREATE FUNCTION group_bulletins_j(integer, integer, integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(gm))
      FROM (SELECT id, gid, uid,
                   content, title, submit_time
              FROM "group_bulletin"
             WHERE gid = $1
             ORDER BY id DESC
             LIMIT $2
            OFFSET $3) gm;
$$ LANGUAGE SQL;

DROP FUNCTION IF EXISTS insert_group_bulletin(integer, integer, varchar, varchar);
CREATE FUNCTION insert_group_bulletin(integer, integer, varchar, varchar)
  RETURNS integer
AS $$
    INSERT INTO "group_bulletin"
           (gid, uid, content, title)
    VALUES ($1, $2, $3, $4)
    RETURNING id;
$$ LANGUAGE SQL;

DROP FUNCTION IF EXISTS update_group_info(integer, varchar, varchar, varchar, varchar);
CREATE FUNCTION update_group_info(integer, varchar, varchar, varchar, varchar)
  RETURNS void
AS $$
    UPDATE "group"
       SET name=$3,
           intro=$4,
           motton=$5
      WHERE gid = $1
        AND founder = $2
$$ LANGUAGE SQL;

--------------------------------------------------------------------------------
-- 触发器
--------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION delete_group_topic() RETURNS trigger AS
$$
BEGIN
    DELETE FROM "group_message" AS gm WHERE gm.reply_id = OLD.id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS "t_delete_group_topic" ON "group_topic";
CREATE TRIGGER "t_delete_group_topic" BEFORE DELETE ON "group_topic"
   FOR EACH ROW EXECUTE PROCEDURE delete_group_topic();


CREATE OR REPLACE FUNCTION delete_group_user() RETURNS trigger AS
$$
BEGIN
    DELETE FROM "group_message" AS gm WHERE gm.gid = OLD.gid OR gm.uid = OLD.uid;
    DELETE FROM "group_topic" AS gt WHERE gt.gid = OLD.gid OR gt.uid = OLD.uid;
    DELETE FROM "group_bulletin" AS gb WHERE gb.gid = OLD.gid OR gb.uid = OLD.uid;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS "t_delete_group_user" ON "group_user";
CREATE TRIGGER "t_delete_group_user" BEFORE DELETE ON "group_user"
   FOR EACH ROW EXECUTE PROCEDURE delete_group_user();


CREATE OR REPLACE FUNCTION delete_group() RETURNS trigger AS
$$
BEGIN
    DELETE FROM "group_message" AS gm WHERE gm.gid = OLD.gid;
    DELETE FROM "group_topic" AS gt WHERE gt.gid = OLD.gid;
    DELETE FROM "group_user" AS gu WHERE gu.gid = OLD.gid;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS "t_delete_group" ON "group";
CREATE TRIGGER "t_delete_group" BEFORE DELETE ON "group"
   FOR EACH ROW EXECUTE PROCEDURE delete_group();


CREATE OR REPLACE FUNCTION delete_user() RETURNS trigger AS
$$
BEGIN
    DELETE FROM "group_user" AS gu WHERE gu.uid = OLD.uid;
    DELETE FROM "user_info" AS ui WHERE ui.uid = OLD.uid;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS "t_delete_user" ON "user";
CREATE TRIGGER "t_delete_user" BEFORE DELETE ON "user"
   FOR EACH ROW EXECUTE PROCEDURE delete_user();
