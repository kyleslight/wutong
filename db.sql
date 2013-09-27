BEGIN;

DROP TABLE IF EXISTS "article";
CREATE TABLE "article" (
  "id" serial NOT NULL PRIMARY KEY,
  "title" text,
  "describe" text,
  "content" text
);

COMMIT;
