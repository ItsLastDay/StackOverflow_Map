#!/usr/bin/env python3

import operator
import csv
import sys
import itertools

'''
Convert .csv files from data.stackexchange query results to matrices.

We can obtain small matrices using data.stackexchange. They
are limited by 50.000 edges.

For example, using query http://data.stackexchange.com/stackoverflow/query/550335/build-a-small-adjacency-matrix-seeded-from-one-tag,
we can build an adjacency matrix "induced" by one tag, in .csv format:
    cnt,Tag1,Tag2
    "241413","1","1"
    "1424","1","2"
    "2792","1","3"
    "773","1","5"
    "260","1","8"

We want to convert it to rows representation.

Usage:
    $0 path_to_input_csv path_to_output_matrix
'''

path_to_csv = sys.argv[1]
path_to_output = sys.argv[2]

with open(path_to_output, 'w') as out_file:
    with open(path_to_csv, 'r', newline='') as input_csv:
        reader = csv.reader(input_csv)

        it = iter(reader)
        next(it)

        for key, raw_row_items in itertools.groupby(it, operator.itemgetter(1)):
            # Store only higher-than-main-diagonal part.
            row_items = ['{},{}'.format(x[2], x[0]) for x in raw_row_items if int(x[2]) > int(key)]
            row_items_repr = ' '.join(row_items)
            print('{}: {}'.format(key, row_items_repr), file=out_file)
