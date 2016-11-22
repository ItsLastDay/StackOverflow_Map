#!/usr/bin/env python3

import os
import os.path
import shutil

import sys
import csv

from PIL import Image, ImageDraw, ImageOps
from collections import namedtuple

from pyqtree import Index

"""
Read a file with <tag_name, x, y> triples and compute an image representation 
for described points.

This script creates so-called "tiles": many small images with grid-like arrangement.
Tiles are well described in http://wiki.openstreetmap.org/wiki/Tiles.


Input parameters:
    1 - path to a tsv-file which describes points
    2 - maximum zoom level for created tiles

Output:
    Writes output tiles to a directory `TILES_DIR`. Deletes everything in it beforehand.
    Tiles are named `x_y_z.png`, where `z` is the zoom level, `x` and `y` are
    tile coordinates (from 0 to 2**z - 1).


Example usage:
    python3 get_tiling.py tsne_output_example.tsv 5
"""

TILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tiles')

Point = namedtuple('Point', ['x', 'y'])

def get_tags_data(tsv_data_path):
    with open(tsv_data_path, newline='') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        tags = []
        for row in reader:
            tags.append(Tag(float(row['x']), float(row['y']), row['name']))

        return tags

class Tag:
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name


class Tiler:
    SHIFT = 10
    BORDER = 1
    TILE_DIM = 256 - BORDER

    def __init__(self, tags, max_tile_size):
        self.max_tile_size = max_tile_size
        
        self.max_x = max((tag.x for tag in tags)) + self.SHIFT
        self.min_x = min((tag.x for tag in tags)) - self.SHIFT

        self.max_y = max((tag.y for tag in tags)) + self.SHIFT
        self.min_y = min((tag.y for tag in tags)) - self.SHIFT

        self.tag_spatial_index = Index(bbox=(self.min_x, self.min_y, self.max_x, self.max_y))
        for tag in tags:
            bbox = (tag.x, tag.y, tag.x, tag.y)
            self.tag_spatial_index.insert(tag, bbox)

        self.origin = Point(self.min_x, self.min_y)
        max_size = max(self.max_x - self.min_x, self.max_y - self.min_y)
        self.size = max_size


    def get_tile(self, x, y, zoom):
        """
        Get one of 2^z * 2^z tiles, with coordinates (x, y) starting from zero.
        """
        im = Image.new('RGB', (self.TILE_DIM, self.TILE_DIM), (200, 200, 200))
        d = ImageDraw.Draw(im)

        size_tile = self.size / (1 << zoom)
        lower_left_corner = Point(self.origin.x + x * size_tile,
                                  self.origin.y + y * size_tile)
        circle_rad = zoom / 2
        cnt_points = 0

        # Match slightly more tags, so that circles from neighbouring tiles can be drawn partially.
        tags_inside_tile = self.tag_spatial_index.intersect((lower_left_corner.x - self.SHIFT, 
                                                             lower_left_corner.y - self.SHIFT,
                                                             lower_left_corner.x + size_tile + self.SHIFT, 
                                                             lower_left_corner.y + size_tile + self.SHIFT))

        for tag in tags_inside_tile:
            x, y = tag.x, tag.y

            # Get coords from tile origin, then scale to TILE_DIM
            point_coords = Point(x - lower_left_corner.x, y - lower_left_corner.y)
            pnt = Point(point_coords.x / size_tile * self.TILE_DIM,
                        point_coords.y / size_tile * self.TILE_DIM)

            if zoom == self.max_tile_size:
                d.text(pnt, tag.name, fill=(0,0,0))
            d.ellipse([pnt.x - circle_rad, pnt.y - circle_rad,
                   pnt.x + circle_rad, pnt.y + circle_rad],
                   fill=(0, 0, 255))
            cnt_points += 1

        return im, cnt_points


def main():
    tsv_data_path = sys.argv[1]
    max_tile_size = int(sys.argv[2]) 
    try:
        shutil.rmtree(TILES_DIR)
    except FileNotFoundError:
        pass
    os.mkdir(TILES_DIR)

    tiler = Tiler(get_tags_data(tsv_data_path), max_tile_size)

    def tile_saver(x, y, tile_size):
        im, cnt_points = tiler.get_tile(x, y, tile_size)
        fname = os.path.join(TILES_DIR, '{}_{}_{}.png'.format(x, y, tile_size))
        im = ImageOps.expand(im, border=Tiler.BORDER,fill='black')
        im.save(fname)

    for tile_size in range(0, max_tile_size + 1):
        print('Generating zoom level =',tile_size)
        all_args = ((x, y, tile_size) for x in range(2 ** tile_size) 
                for y in range(2 ** tile_size))
        for args in all_args:
            tile_saver(*args)

if __name__ == '__main__':
    main()
