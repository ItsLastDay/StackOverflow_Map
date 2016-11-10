#!/usr/bin/env python3

import csv
from PIL import Image, ImageDraw
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])

def get_points_data():
    with open('tsne_out.tsv', newline='') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        return [row for row in reader]


class TilerDurden:
    SHIFT = 10
    TILE_DIM = 256

    def __init__(self, points):
        for point in points:
            point['x'] = float(point['x'])
            point['y'] = float(point['y'])

        self.points = points #  A list of dicts with 'name', 'x', 'y'

        self.max_x = max((point['x'] for point in points)) + self.SHIFT
        self.min_x = min((point['x'] for point in points)) - self.SHIFT

        self.max_y = max((point['y'] for point in points)) + self.SHIFT
        self.min_y = min((point['y'] for point in points)) - self.SHIFT

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
        upper_left_corner = Point(self.origin.x + x * size_tile,
                                  self.origin.y + y * size_tile)
        circle_rad = zoom / 2
        cnt_points = 0

        # TODO: query a quadtree for a square slightly larger than current one
        # (so that arcs and text are not interrupted). Draw everything
        # in a loop.
        for point in self.points:
            x, y = point['x'], point['y']
            if not (upper_left_corner.x <= x <= upper_left_corner.x + size_tile):
                continue

            if not (upper_left_corner.y <= y <= upper_left_corner.y + size_tile):
                continue

            # Get coords from tile origin, then scale to TILE_DIM
            point_coords = Point(x - upper_left_corner.x, y - upper_left_corner.y)
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
    tiler = TilerDurden(get_points_data())

    tile_size = 2
    for y in range(2 ** tile_size):
        for x in range(2 ** tile_size):
            im, cnt_points = tiler.get_tile(x, y, tile_size)
            if cnt_points > 1000:
                im.show()
