#!/usr/bin/env python3

'''
Graph2vec requires an adjacency list of a graph.

We have an adjacency matrix, which stores inverses
of distances. Convert it to an adjacency list 
in the following way:
    a[i][j] = 0 => no edge between i and j
    a[i][j] = k > 0 => edge (i, j) with length equal to 1000/k
            (multiplied by 1000 so that distances are not too small)

Input (hardcoded path): 
    A file with the adjacency matrix, only higher-than-main-diagonal part, like this:
    1: 3517,1
    2:
    3: 41,2 44,1 54836,1
    4: 37043,1 44404,1
    5:
    6:
    ...

Output (to stdout):
    A file with the adjacency list, like this:
    1 3517 1000
    3 41 500
    3 44 1000
    ...
'''

DATA_DIR = '../../data'

matrix_file = '{}/precomp_matrix_2/matrix.txt'.format(DATA_DIR)

with open(matrix_file, 'r') as matrix:
    for line in matrix:
        vertex_from, edges = line.split(':')
        edges = edges.strip()
        if not edges:
            continue

        for edge in edges.strip().split(' '):
            vertex_to, raw_dist = edge.split(',')
            dist = 1000 / int(raw_dist)

            print(vertex_from, vertex_to, dist)
            # Graph2Vec thinks that graph is directed.
            print(vertex_to, vertex_from, dist)
