DROP TABLE IF EXISTS "user" CASCADE;
CREATE TABLE "user" (
    id serial NOT NULL PRIMARY KEY,
    email varchar(50) NOT NULL,
    password varchar(128) NOT NULL,
    name varchar(32) NOT NULL,
    realname varchar(32) NOT NULL DEFAULT '',
    register_date timestamp NOT NULL DEFAULT now(),
    total_grade int NOT NULL DEFAULT 0
);

DROP TABLE IF EXISTS "user_info" CASCADE;
CREATE TABLE "user_info" (
    id serial REFERENCES "user"(id),
    -- true == male, false == female
    sex bool NOT NULL,
    age smallint NOT NULL,
    position text,
    motton varchar(200)
    -- avatar,
);

DROP TABLE IF EXISTS "artical" CASCADE;
CREATE TABLE "artical" (
    id serial NOT NULL PRIMARY KEY,
    title varchar(50) NOT NULL,
    body text NOT NULL,
    submit_time timestamp NOT NULL DEFAULT now()
);

DROP TABLE IF EXISTS "group" CASCADE;
CREATE TABLE "group" (
    id serial NOT NULL PRIMARY KEY,
    name varchar(32),
    found_time timestamp NOT NULl DEFAULT now(),
    motton text
);
