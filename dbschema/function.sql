--------------------------------------------------------------------------------
-- 函数
--------------------------------------------------------------------------------

-- 用户详细信息
DROP FUNCTION IF EXISTS f_get_user_info_j(integer);
CREATE FUNCTION f_get_user_info_j(integer)
  RETURNS json
AS $$
    SELECT row_to_json(row(u))
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
DROP FUNCTION IF EXISTS f_register_user(varchar, varchar, varchar);
CREATE FUNCTION f_register_user(varchar, varchar, varchar)
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
DROP FUNCTION IF EXISTS f_activate_user(varchar);
CREATE FUNCTION f_activate_user(varchar)
  RETURNS integer AS
$$
    UPDATE "user"
       SET ("is_activated") = (true)
     WHERE md5(CAST("uid" AS varchar)) = $1
    RETURNING "uid";
$$ LANGUAGE SQL;

-- 用户登录, return uid
DROP FUNCTION IF EXISTS f_user_login(varchar, varchar);
CREATE FUNCTION f_user_login(varchar, varchar)
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
DROP FUNCTION IF EXISTS f_get_uid(varchar);
CREATE FUNCTION f_get_uid(varchar)
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
DROP FUNCTION IF EXISTS f_get_group_info_j(integer);
CREATE FUNCTION f_get_group_info_j(integer)
  RETURNS json
AS $$
    SELECT row_to_json(row(g))
      FROM (
           SELECT gid, name, founder,
                  intro, motton, publicity,
                  foundtime
             FROM "group"
             WHERE gid = $1
        ) g;
$$ LANGUAGE SQL;

-- 创建小组, return gid
DROP FUNCTION IF EXISTS f_create_group(varchar, varchar, varchar, varchar);
CREATE FUNCTION f_create_group(varchar, varchar, varchar, varchar)
  RETURNS integer
AS $$
    INSERT INTO "group"
           ("name", "founder", "intro", "motton")
    VALUES ($1, $2, $3, $4)
    RETURNING gid;
$$ LANGUAGE SQL;

-- 加入小组
DROP FUNCTION IF EXISTS f_join_group(integer, integer);
CREATE FUNCTION f_join_group(integer, integer)
  RETURNS void
AS $$
    INSERT INTO "group_user"
           ("gid", "uid")
    VALUES ($1, $2);
$$ LANGUAGE SQL;
--------------------------------------------------------------------------------
DROP FUNCTION IF EXISTS f_get_group_messages_j(integer, integer, integer);
CREATE FUNCTION f_get_group_messages_j(integer, integer, integer)
  RETURNS json
AS $$
    SELECT array_to_json(array_agg(gm))
      FROM (SELECT id, gid, uid,
                   content, title, reply_id,
                   submit_time
              FROM "group_message"
             WHERE gid = $1
             LIMIT $2
            OFFSET $3) gm;
$$ LANGUAGE SQL;

DROP FUNCTION IF EXISTS f_insert_group_message(integer, integer, varchar, varchar, integer);
CREATE FUNCTION f_insert_group_message(integer, integer, varchar, varchar, integer)
  RETURNS void
AS $$
    INSERT INTO "group_message"
           (gid, uid, content,
            title, reply_id)
    VALUES ($1, $2, $3, $4, $5)
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION f_delete_user() RETURNS trigger AS
$$
BEGIN
    DELETE FROM "user_info" AS ui WHERE ui.uid = OLD.uid;
    DELETE FROM "group_user" AS gu WHERE gu.uid = OLD.uid;
    DELETE FROM "group_message" AS gm WHERE gm.uid = OLD.uid;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION f_delete_group() RETURNS trigger AS
$$
BEGIN
    DELETE FROM "group_user" AS gu WHERE gu.gid = OLD.gid;
    DELETE FROM "group_message" AS gm WHERE gm.gid = OLD.gid;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;
--------------------------------------------------------------------------------
-- 触发器
--------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS "t_delete_user" ON "user";
CREATE TRIGGER "t_delete_user" BEFORE DELETE ON "user"
   FOR EACH ROW EXECUTE PROCEDURE f_delete_user();


DROP TRIGGER IF EXISTS "t_delete_group" ON "group";
CREATE TRIGGER "t_delete_group" BEFORE DELETE ON "group"
   FOR EACH ROW EXECUTE PROCEDURE f_delete_group();
