#!/usr/bin/env python3

'''
There are two main mappings: 
    from id in adjacency matrix to id in neighbour matrix
    from id in adjacency matrix to tag name
Also, we can have as many additional mappings as we wish (from
id in adjacency matrix to something, e.g. to post count for this tag).

Since the neighbour matrix is input for t-SNE, we need
to make mapping from neighbour matrix id to tag name.

Input:
    1 - path to mapping from adj. matrix to neighbour matrix
        1 0
        2 1
        3 2
        5 3
        8 4
        9 5
        ...
    2,... - paths to mappings from adj.matrix to some value (e.g. tag name) (in .csv)
        id,TagName
        "1",".net"
        "2","html"
        "3","javascript"
        "4","css"
        "5","php"
        "8","c"
        "9","c#"

Output:
    Print a combined .csv file to stdout, indexed by id in neighbour matrix.
        0 .net
        1 html
        2 javascript
        3 php
        4 c
        5 c#
'''

import sys
import csv
from collections import defaultdict


path_to_adj_to_neighbour = sys.argv[1]

adj_to_properties_mapping = defaultdict(list)

header = ['Id']
with open(path_to_adj_to_neighbour, 'r') as inp_adj_to_neighbour:
    for line in inp_adj_to_neighbour:
        adj_id, n_id = map(int, line.split())
        adj_to_properties_mapping[adj_id].append(n_id)

for path_to_property in sys.argv[2:]:
    with open(path_to_property, 'r', newline='') as adj_to_property:
        reader = csv.reader(adj_to_property)
        
        for i, row in enumerate(reader):
            if i == 0:
                cur_header = row
                assert(cur_header[0].lower() == 'id')
                # Unify `name` property names.
                if cur_header[1] in ('TagName', 'Tag'):
                    cur_header[1] = 'name'
                header.append(cur_header[1])
                continue

            adj_id, prop = row
            adj_id = int(adj_id)
            if adj_id in adj_to_properties_mapping:
                adj_to_properties_mapping[adj_id].append(prop)

print(','.join(header))
for val in sorted(adj_to_properties_mapping.values(), key = lambda x: x[0]):
    print(','.join(map(str, val)))
