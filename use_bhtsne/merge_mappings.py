#!/usr/bin/env python3

'''
There are two mappings: 
    from id in adjacency matrix to id in neighbour matrix
    from id in adjacency matrix to tag name

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
    2 - path to mapping from adj.matrix to tag name (in .csv)
        id,TagName
        "1",".net"
        "2","html"
        "3","javascript"
        "4","css"
        "5","php"
        "8","c"
        "9","c#"

Output:
    Print pairs <neighbour matrix id, tag name> to stdout.
        0 .net
        1 html
        2 javascript
        3 php
        4 c
        5 c#
'''

import sys
import csv


path_to_adj_to_neighbour = sys.argv[1]
path_to_adj_to_tag = sys.argv[2]

adj_to_n_mapping = dict()

with open(path_to_adj_to_neighbour, 'r') as inp_adj_to_neighbour:
    for line in inp_adj_to_neighbour:
        adj_id, n_id = map(int, line.split())
        adj_to_n_mapping[adj_id] = n_id

with open(path_to_adj_to_tag, 'r', newline='') as inp_adj_to_tag:
    reader = csv.reader(inp_adj_to_tag)
    
    for i, row in enumerate(reader):
        if i == 0:
            continue
        adj_id, tag_name = row
        adj_id = int(adj_id)
        if adj_id in adj_to_n_mapping:
            print(adj_to_n_mapping[adj_id], tag_name)





