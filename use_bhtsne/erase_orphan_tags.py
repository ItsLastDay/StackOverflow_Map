#!/usr/bin/env python3

import sys

'''
Some tags are orphaned: they are (nearly) disconnected
from the rest of the graph.

Therefore they neighbour list looks either like this
    3:
or like this:
    32031: 32032,144.27 32033,144.27 32034,144.27 32035,144.27 32036,144.27 54259,288.539

So, if there are fewer entries than needed, we need to delete this row.
To check this, just count the number of ',' in the row.


Arguments:
    1 - path to file with neighbour information
    2 - needed number of neighbours
'''


need_neighbours = int(sys.argv[2])

with open(sys.argv[1], 'r') as neighbour_matrix:
    for line in neighbour_matrix:
        if line.count(',') != need_neighbours:
            continue
        print(line, end='')
