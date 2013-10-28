DROP TABLE IF EXISTS test;

CREATE TABLE test (
  "id" serial NOT NULL PRIMARY KEY,
  "ip" varchar(200) NOT NULL,
  "submit_time" timestamp NOT NULL DEFAULT now(),
  "content" text NOT NULL
);

