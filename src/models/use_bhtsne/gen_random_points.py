#!/usr/bin/env python3

import random
import sys

'''
Generate random points to see similarity values in bhtsne.

Usage:
    $0 num_points num_dims sparsity
'''

n = int(sys.argv[1])
dims = int(sys.argv[2])
sparsity = float(sys.argv[3])

for i in range(n):
    print('\t'.join(map(str, [random.randint(-n * sparsity, n * sparsity) for j in range(dims)])))
