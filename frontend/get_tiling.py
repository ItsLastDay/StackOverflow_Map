#!/usr/bin/env python3

import csv
from PIL import Image, ImageDraw
from collections import namedtuple

from pyqtree import Index

Point = namedtuple('Point', ['x', 'y'])

def get_tags_data():
    with open('tsne_out.tsv', newline='') as tsvfile:
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


class TilerDurden:
    SHIFT = 10
    TILE_DIM = 256

    def __init__(self, tags):
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
        im = Image.new('RGB', (self.TILE_DIM, self.TILE_DIM), (255, 255, 255))
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

            if zoom >= 7:
                d.text(pnt, point['name'], fill=(0,0,0))
            d.ellipse([pnt.x - circle_rad, pnt.y - circle_rad,
                   pnt.x + circle_rad, pnt.y + circle_rad],
                   fill=(0, 0, 255))
            cnt_points += 1

        return im, cnt_points


if __name__ == '__main__':
    tiler = TilerDurden(get_tags_data())

    tile_size = 4
    for y in range(2 ** tile_size):
        for x in range(2 ** tile_size):
            im, cnt_points = tiler.get_tile(x, y, tile_size)
            fname = '{}_{}_{}.png'.format(x, y, tile_size)
            im.save(fname)
