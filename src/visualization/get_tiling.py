#!/usr/bin/env python3

import os
import os.path
import shutil

import sys
import csv

import heapq
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

from tiler import DarkTiler, Tag


"""
Read a file with <tag_name, x, y> triples and compute an image representation 
for described points.

This script creates so-called "tiles": many small images with grid-like arrangement.
Tiles are well described in http://wiki.openstreetmap.org/wiki/Tiles.

This routine saves tiles according into folder parametrized by 
input date. This date means the lowest date of any post that
is used to compute tag similarity. This way, you can save
multiple maps (referring to multiple dates) and compare them.


Input parameters:
    1 - path to a tsv-file which describes points
    2 - path to a csv-file with additional information about points
    3 - maximum zoom level for created tiles
    4 - lower bound on a date of any post that is used to compute tag similarity.

Output:
    Writes output tiles to a directory `TILES_DIR_BASE` with appended posts date.
    Deletes everything in it beforehand.
    Tiles are named `x_y_z.png`, where `z` is the zoom level, `x` and `y` are
    tile coordinates (from 0 to 2**z - 1).


Example usage:
    python3 get_tiling.py tsne_output_example.tsv id_to_additional_info_example.csv 5 example
"""

TILES_DIR_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, os.path.pardir,'data','tiles', 'tiles')

# Each tile is rendered in (256x256)*ANTIALIASING_SCALE size,
# and then downscaled with antialiasing.
# http://stackoverflow.com/questions/14350645/is-there-antialiasing-method-for-python-pil
ANTIALIASING_SCALE = 1
TILE_DIM = 256 * ANTIALIASING_SCALE
# SHIFT is used for ensuring that any geometry on the border of two tiles
# is drawn properly.
SHIFT = 10 * ANTIALIASING_SCALE
# Tiles are united in groups of METATILE_SIZE x METATILE_SIZE units.
METATILE_SIZE = 8
# The level, starting at which all tag names are shown, and number of shown tag 
# names per tile.
ZOOM_TEXT_SHOW = 7
TAGS_ANNOTATED_PER_TILE = 10

Point = namedtuple('Point', ['x', 'y'])


def get_tags_data(tsv_data_path, additional_data_path):
    with open(additional_data_path, 'r', newline='') as additional_info_file:
        additional_reader = csv.DictReader(additional_info_file)
        with open(tsv_data_path, 'r', newline='') as tsvfile:
            reader = csv.DictReader(tsvfile, delimiter='\t')
            tags = []
            for row, add_info in zip(reader, additional_reader):
                flat_addinfo = [(name, add_info[name]) for name in additional_reader.fieldnames]
                tags.append(Tag(float(row['x']), float(row['y']), *flat_addinfo))

            return tags




def get_tile_dir(date_suffix):
    return '{}_{}'.format(TILES_DIR_BASE, date_suffix)


def prepare_tile_dir(tile_dir):
    try:
        shutil.rmtree(tile_dir)
    except FileNotFoundError:
        pass
    os.mkdir(tile_dir)


def render_tiles(img, meta_x, meta_y, tile_zoom, tile_dir):
    for dx in range(METATILE_SIZE):
        x = meta_x + dx
        if x >= 2 ** tile_zoom:
            break

        for dy in range(METATILE_SIZE):
            y = meta_y + dy
            if y >= 2 ** tile_zoom:
                break

            img_name = os.path.join(tile_dir, '{}_{}_{}.png'.format(x, y, tile_zoom))

            image_part = img.crop((dx * TILE_DIM, dy * TILE_DIM, 
                                    (dx + 1) * TILE_DIM, (dy + 1) * TILE_DIM))

            image_part = image_part.resize((TILE_DIM // ANTIALIASING_SCALE,
                                            TILE_DIM // ANTIALIASING_SCALE),
                                            resample=Image.LANCZOS)

            image_part.save(img_name, optimize=True)

    del img


def main():
    tsv_data_path = sys.argv[1]
    additional_data_path = sys.argv[2]
    max_tile_zoom = int(sys.argv[3])
    date_suffix = sys.argv[4]

    tile_dir = get_tile_dir(date_suffix)
    prepare_tile_dir(tile_dir)

    tiler = DarkTiler(get_tags_data(tsv_data_path, additional_data_path))
    pool = ThreadPoolExecutor()


    for tile_zoom in range(0, max_tile_zoom + 1):
        print('Generating zoom level =', tile_zoom)
        for meta_x in range(0, 1 << tile_zoom, METATILE_SIZE):
            for meta_y in range(0, 1 << tile_zoom, METATILE_SIZE):
                img, cnt_points = tiler.get_metatile(meta_x, meta_y, tile_zoom)
                pool.submit(render_tiles, img, meta_x, meta_y, tile_zoom, tile_dir)


    pool.shutdown(wait=True)


if __name__ == '__main__':
    main()
