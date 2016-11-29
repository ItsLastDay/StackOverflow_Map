#!/bin/bash

# $1 = file with neighbour matrix
neighbours_file=$1

tmp_inp_file=$(mktemp)

n=$(cat "$neighbours_file" | wc -l)
dims=0
theta=0.3
perplexity=30
no_dims=2
max_iter=10000

printf "%d %d %f %d %d %d\n" "$n" "$dims" "$theta" "$perplexity" "$no_dims" "$max_iter" > "$tmp_inp_file"
cat "$neighbours_file" >> "$tmp_inp_file"

# http://stackoverflow.com/a/4774063/5338270
pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd`
popd > /dev/null

${SCRIPTPATH}/bh_tsne < "$tmp_inp_file"
