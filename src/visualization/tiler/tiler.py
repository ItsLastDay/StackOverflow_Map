# -*- coding: utf-8 -*-

import os
from collections import namedtuple
import abc
import typing

from pyqtree import Index
from PIL import Image

# Each tile is rendered in (256x256)*ANTIALIASING_SCALE size,
# and then downscaled with antialiasing.
# http://stackoverflow.com/questions/14350645/is-there-antialiasing-method-for-python-pil
ANTIALIASING_SCALE = 4
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
                                            resample=Image.ANTIALIAS)

            image_part.save(img_name, optimize=True)

    del img


class Tag:
    def __init__(self, x, y, *additional_info):
        self.x = x
        self.y = y
        for field_name, field_val in additional_info:
            self.__dict__[field_name] = field_val


class Tiler(abc.ABC):
    def set_extent(self, tags):
        self.max_x = max((tag.x for tag in tags)) + SHIFT
        self.min_x = min((tag.x for tag in tags)) - SHIFT

        self.max_y = max((tag.y for tag in tags)) + SHIFT
        self.min_y = min((tag.y for tag in tags)) - SHIFT

        self.origin = Point(self.min_x, self.min_y)
        max_size = max(self.max_x - self.min_x, self.max_y - self.min_y)
        self.map_size = max_size

        self.tile_size = [self.map_size / (1 << i) * METATILE_SIZE for i in range(20)]

        self.tag_to_normpos = dict()
        for tag in tags:
            x, y = tag.x, tag.y
            rel_x, rel_y = x - self.origin.x, y - self.origin.y
            norm_x, norm_y = rel_x / self.map_size, rel_y / self.map_size
            self.tag_to_normpos[tag.name] = (norm_x, norm_y)

    def set_bbox(self, tags):
        self.tag_spatial_index = Index(bbox=(self.min_x, self.min_y, self.max_x, self.max_y))
        for tag in tags:
            bbox = (tag.x, tag.y, tag.x, tag.y)
            self.tag_spatial_index.insert(tag, bbox)

    def set_postcount(self, tags):
        for tag in tags:
            tag.PostCount = int(getattr(tag, 'PostCount', -1))
        self.max_post_count = max(int(tag.PostCount) for tag in tags)

    def set_fonts(self):
        pass

    def __init__(self, tags):
        self.set_extent(tags)
        self.set_bbox(tags)
        self.set_postcount(tags)
        self.set_fonts()

    def search(self, name):
        return self.tag_to_normpos.get(name, '')

    @abc.abstractmethod
    def get_postcount_measure(self, tag: Tag):
        pass

    def get_tags_in_tile(self, meta_x, meta_y, zoom, with_shift):
        tile_size = self.tile_size[zoom]
        lower_left_corner = Point(self.origin.x + meta_x * tile_size,
                                  self.origin.y + meta_y * tile_size)

        shift = SHIFT if with_shift else 0
        tags_inside_tile = self.tag_spatial_index.intersect((lower_left_corner.x - shift,
                                                             lower_left_corner.y - shift,
                                                             lower_left_corner.x + tile_size + shift,
                                                             lower_left_corner.y + tile_size + shift))

        return tags_inside_tile

    @abc.abstractmethod
    def get_names_of_shown_tags(self, meta_x, meta_y, zoom) -> set:
        """
        Return the names of tags that we will show on the map.
        """
        raise NotImplemented

    @abc.abstractmethod
    def get_metatile(self, meta_x, meta_y, zoom):
        '''
        Get 8x8 rectangle of tiles, compute them at once.
        This is faster than computing them one-by-one.

        `meta_x` and `meta_y` are coordinates of upper-left tile of the
        generated metatile.

        :return img, cnt_points tuple where img is Image, and cnt_point number of points on it.
        '''
        raise NotImplemented
