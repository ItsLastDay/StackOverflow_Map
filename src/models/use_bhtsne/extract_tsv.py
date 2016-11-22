#!/usr/bin/env python3

import sys
import os.path

# Leave only tab-separated triples <tag_name, x, y>

# 1 = path to t-SNE output

def main():
    raw_output_fname = os.path.abspath(sys.argv[1])
    START_INFO = '######START TSV'
    END_INFO = '######END TSV'

    occured_start = False
    with open(raw_output_fname, 'r') as raw_output:
        for row in raw_output:
            row = row.strip()
            if row == END_INFO:
                occured_start = False
            if occured_start:
                print(row)
            if row == START_INFO:
                occured_start = True


if __name__ == '__main__':
    main()
