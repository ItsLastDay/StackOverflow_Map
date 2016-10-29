#!/bin/bash

g++ -std=c++11 -Wall -Werror -O3 ./compute_nearest_neighbours.cpp -o result

# $1 = path to matrix
# $2 = number of neighbours
# $3 = path to output file with converted mapping
./result $1 $2 $3
