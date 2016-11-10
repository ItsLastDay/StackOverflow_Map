#!/bin/bash

g++ -o bh_tsne -std=c++11 -O2 tsne.cpp sptree.cpp || exit 1

# $1 = file with neighbour matrix
# $2 = file with mapping from id to tag name
neighbours_file=$1
mapping_file=$2

tmp_inp_file=$(mktemp)

n=$(cat "$neighbours_file" | wc -l)
dims=0
theta=0.3
perplexity=30
no_dims=2
max_iter=17000

printf "%d %d %f %d %d %d\n" "$n" "$dims" "$theta" "$perplexity" "$no_dims" "$max_iter" > "$tmp_inp_file"
cat "$mapping_file" >> "$tmp_inp_file"
cat "$neighbours_file" >> "$tmp_inp_file"

./bh_tsne < "$tmp_inp_file"
