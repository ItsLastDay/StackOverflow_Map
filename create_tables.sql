-- Create tables in PostgreSQL DBMS.

DROP TABLE IF EXISTS PostTag;
DROP TABLE IF EXISTS Posts;
DROP TABLE IF EXISTS Tags;

CREATE TABLE Posts
(
    Id bigint PRIMARY KEY NOT NULL,
    CreationDate timestamp
);

CREATE TABLE Tags
(
    Id integer PRIMARY KEY NOT NULL,
    Name varchar(25)
);

CREATE TABLE PostTag
(
    PostId bigint REFERENCES Posts (Id),
    TagId integer REFERENCES Tags (Id),

    PRIMARY KEY (PostId, TagId)
);

