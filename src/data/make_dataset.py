#!/usr/bin/env python3

import gzip
import urllib.request
import os.path
import shutil

'''
Download raw data from `StackLite` repository.
It contains metainformation about questions and
about relations of questions and tags.

Warning: uncompressed data weights about 1Gb,
so make sure not to run this script too often.

We could write this using Bash script, but Python
seem more cross-platform. 
Also, Python support
for gzip is increasing from version to version,
which looks promising.

Example usage:
    python3 make_dataset.py
'''

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
RAW_DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../data/raw'))
STACKLITE_BASE_URL = 'https://github.com/dgrtwo/StackLite/raw/master'

def main():
    print('Getting raw tag data from StackLite repo...')

    # About copying remote files via urllib.request:
    # http://stackoverflow.com/a/7244263/5338270
    
    for filename in ('question_tags.csv.gz', 'questions.csv.gz'):
        download_url = '{}/{}'.format(STACKLITE_BASE_URL, filename)
        file_path = os.path.join(RAW_DATA_DIR, filename)

        print('Downloading {}'.format(filename))
        with urllib.request.urlopen(download_url) as response:
            with open(file_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)

        print('Decompressing {}'.format(filename))
        with gzip.open(file_path, 'rb') as compressed_file:
            out_filename = filename[:-len('.csv.gz')] + '.csv'
            out_file_path = os.path.join(RAW_DATA_DIR, out_filename)

            with open(out_file_path, 'wb') as out_file:
                shutil.copyfileobj(compressed_file, out_file)

    print('Successfully obtained raw data')

if __name__ == '__main__':
    main()
