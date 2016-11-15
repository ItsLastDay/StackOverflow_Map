#!/usr/bin/env python3

import csv
import os.path

'''
Take StackOverflow data from https://github.com/dgrtwo/StackLite:
    questions.csv
        Id,CreationDate,ClosedDate,DeletionDate,Score,OwnerUserId,AnswerCount
        4,2008-07-31T21:42:52Z,NA,NA,418,8,13
        6,2008-07-31T22:08:08Z,NA,NA,188,9,5
        ...
    question_tags.csv
        Id,Tag
        4,winforms
        4,type-conversion
        4,decimal
        4,opacity
        ...

From questions, wer need only Id and CreationDate -> delete everything else.

From tags, we need to make Id-s:
    1,c#
    2,winforms
    ...
Then, convert question_tags into having post_id and tag_id (instead of post_id and 
tag name).


Output:
    posts.csv
        Id,CreationDate
        4,2008-07-31T21:42:52Z
        6,2008-07-31T22:08:08Z
        ...
    tags.csv
        Id,Tag
        1,c#
        2,winforms
        ...
    post_tag.csv
        PostId,TagId
        1,4
        1,5
        2,8
        ...


Time: ~7min
'''

REPO_DIR = os.path.abspath(os.path.dirname(__file__))
RAW_DATA_DIR = os.path.join(REPO_DIR, '../../data/raw')
INTERIM_DATA_DIR = os.path.join(REPO_DIR, '../../data/interim')

tag_to_id_mapping = dict()


with open(os.path.join(RAW_DATA_DIR, 'questions.csv'), 'r', newline='') as questions_file:
    reader = csv.reader(questions_file)
    with open(os.path.join(INTERIM_DATA_DIR, 'posts.csv'), 'w', newline='') as posts_csv_file:
        # We could use DictWriter, but it is slower.
        writer = csv.writer(posts_csv_file)
        for i, row in enumerate(reader):
            if i == 0:
                writer.writerow(['Id', 'CreationDate'])
                continue
            post_id = row[0]
            creation_date = row[1]
            writer.writerow([post_id, creation_date])


with open(os.path.join(RAW_DATA_DIR, 'question_tags.csv'), 'r', newline='') as question_tags_file:
    reader = csv.reader(question_tags_file)
    all_tags = set()

    for row in reader:
        all_tags.add(row[1])
    all_tags.remove('Tag')

    tags = list(sorted(all_tags))

    with open(os.path.join(INTERIM_DATA_DIR, 'tags.csv'), 'w', newline='') as tags_csv_file:
        writer = csv.writer(tags_csv_file)
        writer.writerow(['Id', 'Tag'])
        for i, tag in enumerate(tags, 1):
            tag_to_id_mapping[tag] = i
            writer.writerow([i, tag])



with open(os.path.join(RAW_DATA_DIR, 'question_tags.csv'), 'r', newline='') as question_tags_file:
    reader = csv.reader(question_tags_file)
    with open(os.path.join(INTERIM_DATA_DIR, 'post_tag.csv'), 'w', newline='') as post_tag_csv_file:
        writer = csv.writer(post_tag_csv_file)
        
        # Queue to erase duplicate entries.
        # We know that all tags for a single question come sequentially
        # in `question_tags.csv`. Some of them may repeat, unfortunately.
        # In order to overcome this, store a queue of last MAX_QUEUE_SIZE entries.
        # If the current <post, tag> pair is already inside queue, do not output it.
        queue = []
        MAX_QUEUE_SIZE = 40 # ~ max number of tags per question.
        
        for i, row in enumerate(reader):
            if i == 0:
                writer.writerow(['PostId', 'TagId'])
                continue
            post_id = row[0]
            tag = row[1]

            if (post_id, tag) not in queue:
                writer.writerow([post_id, tag_to_id_mapping[tag]])
            queue.append((post_id, tag))
            if len(queue) > MAX_QUEUE_SIZE:
                queue.pop(0)





