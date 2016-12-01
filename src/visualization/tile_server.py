from flask import Flask, send_from_directory, make_response

import re
import io
import random

import os
import os.path

import get_tiling


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__));
PROCESSED_DIR = os.path.join(BASE_DIR, '../../data/processed/')

POINTS_TSV_FMT = os.path.join(BASE_DIR, 'tsne_output_{}.tsv')
ADDITIONAL_INFO_FMT = os.path.join(PROCESSED_DIR, 'id_to_additional_info_{}.csv')


tile_cache = dict()
MAX_CACHE_SIZE = 256


def get_key(suffix, x, y, z):
    return hash('{}{}{}{}'.format(suffix, x, y, z))

def cache_get(suffix, x, y, z):
    key = get_key(suffix, x, y, z)
    return tile_cache.get(key, None)

def cache_put(suffix, x, y, z, img):
    key = get_key(suffix, x, y, z)
    if key in tile_cache:
        return
    if len(tile_cache) > MAX_CACHE_SIZE:
        tile_cache.pop(random.choice(tile_cache.keys()))

    tile_cache[key] = img


def get_tiler(tiling_suffix, created_tilers=dict()):
    '''
    Given a string like 'tiles_2016-10-10', return an appropriate get_tiling.Tiler object.

    Store already created Tiler-s in a dict.
    '''
    if tiling_suffix not in created_tilers:
        tsv_concrete_name = POINTS_TSV_FMT.format(tiling_suffix)
        additional_info_concrete_name = ADDITIONAL_INFO_FMT.format(tiling_suffix)

        assert os.path.isfile(tsv_concrete_name)
        assert os.path.isfile(additional_info_concrete_name)

        points_data = get_tiling.get_tags_data(tsv_concrete_name, additional_info_concrete_name)
        created_tilers[tiling_suffix] = get_tiling.Tiler(points_data, 0)

    return created_tilers[tiling_suffix]



@app.route('/get_tile_variants')
def tile_variants():
    lst_files = os.listdir()
    tiling_names = []
    # Search for directories starting with 'tiles_' substring.
    for dirname in lst_files:
        if not os.path.isdir(dirname):
            continue
        if not dirname.startswith('tiles_'):
            continue

        tiling_names.append(dirname)

    return '<br>'.join(tiling_names)


@app.route('/cache_size')
def show_cache_size():
    return str(len(tile_cache))


def get_regular_tile(suffix, x, y, z):
    tiler = get_tiler(suffix)

    img, cnt_points = tiler.get_tile(x, y, z)
    
    str_file = io.BytesIO()
    img.save(str_file, format='png')

    response = make_response(str_file.getvalue())
    response.mimetype = 'image/png'

    return response


def get_mt_part(x, y, img):
    mt_size = get_tiling.METATILE_SIZE
    shift_x = x % mt_size
    shift_y = y % mt_size
    t_dim = get_tiling.TILE_DIM

    cropped = img.crop((shift_x * t_dim,
                        shift_y * t_dim,
                        shift_x * t_dim + t_dim,
                        shift_y * t_dim + t_dim
                        ))

    str_file = io.BytesIO()
    cropped.save(str_file, format='png')

    response = make_response(str_file.getvalue())
    response.mimetype = 'image/png'

    return response


def get_metatile_part(suffix, x, y, z):
    tiler = get_tiler(suffix)
    mt_size = get_tiling.METATILE_SIZE

    mt_x = x // mt_size
    mt_y = y // mt_size

    cached = cache_get(suffix, mt_x, mt_y, z)
    if cached:
        return get_mt_part(x, y, cached)

    print('Drawing a metatile', mt_x, mt_y)

    img, cnt_points = tiler.get_metatile(mt_x, mt_y, z)

    cache_put(suffix, mt_x, mt_y, z, img)
    return get_mt_part(x, y, img)
    


@app.route('/tiles_<suffix>/<int:x>_<int:y>_<int:z>.png')
def serve_tile(suffix, x, y, z):
    assert (suffix == 'example' or re.match('^\d{4}-\d{2}-\d{2}$', suffix))

    if z <= 0:
        return get_regular_tile(suffix, x, y, z)
    else:
        return get_metatile_part(suffix, x, y, z)


@app.route('/visualize')
def show_visualization():
    return send_from_directory('', 'tiling_visualizer.html')
