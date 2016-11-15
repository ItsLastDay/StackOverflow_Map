#!/usr/bin/env python3

import pg
import os
from config import get_config_param

'''
There should be 3 tables in PostgreSQL DMBS:
    Posts
        id
        creationDate
    PostTag
        postId
        tagId
    Tags
        id
        name

Populate the tables with prepared StackLite data,
from csv files posts.csv, tags.csv, post_tag.csv
(which are created by `prepare_stacklite_data.py`).

Time: ~30 min.
'''

DATA_DIR = '../../data'

db = pg.DB(
        dbname=get_config_param('db_name'),
        user=get_config_param('db_user'),
        passwd=get_config_param('db_password')
        )

posts_csv = os.path.abspath('{}/posts.csv'.format(DATA_DIR))
tags_csv = os.path.abspath('{}/tags.csv'.format(DATA_DIR))
post_tags_csv = os.path.abspath('{}/post_tag.csv'.format(DATA_DIR))

db.query("COPY Posts FROM '{}' (FORMAT csv, HEADER);".format(posts_csv))
db.query("COPY Tags FROM '{}' (FORMAT csv, HEADER);".format(tags_csv))
db.query("COPY PostTag FROM '{}' (FORMAT csv, HEADER);".format(post_tags_csv))
