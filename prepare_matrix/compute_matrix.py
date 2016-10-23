#!/usr/bin/env python3

import subprocess
import pg
from multiprocessing import Pool
from config import get_config_param

'''
Precompute and save adjacency matrix for all tags.

Current version works in 50min per 1000 rows.
'''



query_row = '''
WITH TaggedPosts AS
(
    SELECT PostId FROM PostTag
    WHERE TagId = {0}
)
SELECT TagId, count(pt.PostId) as cnt
FROM
    TaggedPosts tpos
    JOIN
    PostTag pt
    ON pt.PostId = tpos.PostId
WHERE
    pt.TagId > {0} 
GROUP BY TagId
ORDER BY TagId
'''

class RowGetter:
    '''
        Get adjacency matrix for tags, row-by-row.
    '''
    def __init__(self):
        self.conn = pg.DB(
                dbname=get_config_param('db_name'),
                user=get_config_param('db_user'),
                passwd=get_config_param('db_password')
                )

    def __call__(self, tag_number):
        query = query_row.format(tag_number)
        row = self.conn.query(query).getresult()
        return row

def get_row_representation(row_results):
    '''
    Return string, which is convenient for recreating the row later.
    '''
    return ' '.join(','.join(map(str, x)) for x in row_results)


# http://stackoverflow.com/questions/10117073/how-to-use-initializer-to-set-up-my-multiprocess-pool
conn = None

def set_global_conn():
    global conn
    conn = pg.DB(
            dbname=get_config_param('db_name'),
            user=get_config_param('db_user'),
            passwd=get_config_param('db_password')
            )

def get_adj_row_newcon(tag_number):
    query = query_row.format(tag_number)
    row = conn.query(query).getresult()
    return row


get_adjacency_matrix_row = RowGetter()


if __name__ == '__main__':
    DATA_DIR = '../../data'
    PRECOMP_DIR = '{}/precomp_matrix'.format(DATA_DIR)
    number_of_tags = int(subprocess.getoutput('wc -l {}/tags.csv'.format(DATA_DIR)).split()[0]) - 1

    already_computed = 35000
    count_up_to = 35000
    
    with open('{}/matrix_{}_{}.txt'.format(PRECOMP_DIR, already_computed + 1, count_up_to), 'w') as matrix:
        args = list(range(already_computed + 1, count_up_to + 1))
        with Pool(initializer=set_global_conn, initargs=()) as p:
            rows = p.map(get_adj_row_newcon, args)
            matrix.write('\n'.join(map(get_row_representation, rows)))
