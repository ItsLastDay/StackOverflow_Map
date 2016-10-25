#!/bin/bash

dims=50
n=3000

g++ -o bh_tsne -std=c++11 -O2 tsne.cpp sptree.cpp || exit 1
../gen_random_points.py $n $dims 1 | ./bhtsne.py -d $dims -t 0.3 --verbose
