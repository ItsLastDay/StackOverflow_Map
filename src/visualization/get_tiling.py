#!/usr/bin/env python3

import os
import os.path
import shutil

import sys
import csv

from PIL import Image, ImageDraw, ImageOps, ImageFont
from collections import namedtuple

from pyqtree import Index

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
    2 - maximum zoom level for created tiles
    3 - lower bound on a date of any post that is used to compute tag similarity.

Output:
    Writes output tiles to a directory `TILES_DIR` with appended posts date.
    Deletes everything in it beforehand.
    Tiles are named `x_y_z.png`, where `z` is the zoom level, `x` and `y` are
    tile coordinates (from 0 to 2**z - 1).


Example usage:
    python3 get_tiling.py tsne_output_example.tsv id_to_additional_info_example.csv 5 example
"""

METATILE_SIZE = 8
TILE_DIM = 512

TILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tiles')

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

class Tag:
    def __init__(self, x, y, *additional_info):
        self.x = x
        self.y = y
        for field_name, field_val in additional_info:
            self.__dict__[field_name] = field_val


class Tiler:
    SHIFT = 10
    BORDER = 0

    def __init__(self, tags, max_tile_size):
        self.max_tile_size = max_tile_size
        
        self.max_x = max((tag.x for tag in tags)) + self.SHIFT
        self.min_x = min((tag.x for tag in tags)) - self.SHIFT

        self.max_y = max((tag.y for tag in tags)) + self.SHIFT
        self.min_y = min((tag.y for tag in tags)) - self.SHIFT

        for tag in tags:
            tag.PostCount = int(getattr(tag, 'PostCount', -1))
        self.max_post_count = max(int(tag.PostCount) for tag in tags)

        self.tag_spatial_index = Index(bbox=(self.min_x, self.min_y, self.max_x, self.max_y))
        for tag in tags:
            bbox = (tag.x, tag.y, tag.x, tag.y)
            self.tag_spatial_index.insert(tag, bbox)

        self.origin = Point(self.min_x, self.min_y)
        max_size = max(self.max_x - self.min_x, self.max_y - self.min_y)
        self.size = max_size

        self.fonts = [ImageFont.truetype('./Verdana.ttf', 50 - zoom * 2) for zoom in range(8 + 1)]

    
    def get_postcount_measure(self, tag):
        tag_count = tag.PostCount
        max_post_count = self.max_post_count
        return tag_count / max_post_count


    def get_metatile(self, x, y, zoom):
        ''' 
        Get 8x8 rectangle of tiles, compute them at once.

        Mostly copy-and-paste from the `get_tile` function.
        '''
        im = Image.new('RGB', (TILE_DIM * METATILE_SIZE, 
            TILE_DIM * METATILE_SIZE), (240, 240, 240))
        d = ImageDraw.Draw(im)

        size_tile = self.size / (1 << zoom) * METATILE_SIZE
        lower_left_corner = Point(self.origin.x + x * size_tile,
                                  self.origin.y + y * size_tile)
        max_circle_rad = zoom * 4
        cnt_points = 0

        # Match slightly more tags, so that circles from neighbouring tiles can be drawn partially.
        tags_inside_tile = self.tag_spatial_index.intersect((lower_left_corner.x - self.SHIFT, 
                                                             lower_left_corner.y - self.SHIFT,
                                                             lower_left_corner.x + size_tile + self.SHIFT, 
                                                             lower_left_corner.y + size_tile + self.SHIFT))

        all_postcounts = sorted([tag.PostCount for tag in tags_inside_tile])
        percentile_cutoff = all_postcounts[max(-10, -len(all_postcounts))]
        percentile_cutoff = max(percentile_cutoff, 0)


        for tag in tags_inside_tile:
            x, y = tag.x, tag.y

            # Get coords from tile origin, then scale to TILE_DIM
            point_coords = Point(x - lower_left_corner.x, y - lower_left_corner.y)
            pnt = Point(point_coords.x / size_tile * TILE_DIM * METATILE_SIZE,
                        point_coords.y / size_tile * TILE_DIM * METATILE_SIZE)

            if zoom >= 7 or tag.PostCount >= percentile_cutoff:
                d.text(pnt, tag.name, fill=(0,0,0), font=self.fonts[zoom])

            post_count_measure = self.get_postcount_measure(tag)
            circle_rad = max(2, max_circle_rad * post_count_measure)

            d.ellipse([pnt.x - circle_rad, pnt.y - circle_rad,
                   pnt.x + circle_rad, pnt.y + circle_rad],
                   fill=(0, 0, 255))
            cnt_points += 1

        return im, cnt_points



    def get_tile(self, x, y, zoom):
        """
        Get one of 2^z * 2^z tiles, with coordinates (x, y) starting from zero.
        """
        im = Image.new('RGB', (TILE_DIM, TILE_DIM), (200, 200, 200))
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
            pnt = Point(point_coords.x / size_tile * TILE_DIM,
                        point_coords.y / size_tile * TILE_DIM)

            if zoom >= 7:
                d.text(pnt, tag.name, fill=(0,0,0))

            red_extent = int(255 * (int(getattr(tag, 'PostCount', 0)) / int(getattr(self, 'max_post_count', 1))))
            d.ellipse([pnt.x - circle_rad, pnt.y - circle_rad,
                   pnt.x + circle_rad, pnt.y + circle_rad],
                   fill=(red_extent, 0, 255))
            cnt_points += 1

        return im, cnt_points


def main():
    global TILES_DIR

    tsv_data_path = sys.argv[1]
    additional_data_path = sys.argv[2]
    max_tile_size = int(sys.argv[3])
    date_suffix = sys.argv[4]
    TILES_DIR += '_' + date_suffix

    try:
        shutil.rmtree(TILES_DIR)
    except FileNotFoundError:
        pass
    os.mkdir(TILES_DIR)

    tiler = Tiler(get_tags_data(tsv_data_path, additional_data_path), max_tile_size)

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
