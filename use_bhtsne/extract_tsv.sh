#!/bin/bash

# Leave only tab-separated triples <tag_name, x, y>

# 1 = path to t-SNE output

cat "$1" | sed -n -e '/######START TSV/,/######END TSV/p' | sed -e '1d;$d'
