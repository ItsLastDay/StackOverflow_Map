from flask import Flask, send_from_directory, make_response

import re

import os
import os.path

import get_tiling


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, '../../data/processed/')

POINTS_TSV_FMT = os.path.join(BASE_DIR, 'tsne_output_{}.tsv')
ADDITIONAL_INFO_FMT = os.path.join(PROCESSED_DIR, 'id_to_additional_info_{}.csv')


tiling_names = []
created_tilers = dict()


@app.before_first_request
def initialize():
    global tiling_names
    lst_files = os.listdir('.')
    # Search for directories starting with 'tiles_' substring.
    for dirname in lst_files:
        if not os.path.isdir(dirname):
            continue
        if not dirname.startswith('tiles_'):
            continue

        tiling_names.append(dirname)

    functioning_names = []
    for tiling_name in tiling_names:
        tiling_suffix = tiling_name[len('tiles_'):]
        tsv_concrete_name = POINTS_TSV_FMT.format(tiling_suffix)
        additional_info_concrete_name = ADDITIONAL_INFO_FMT.format(tiling_suffix)

        if not os.path.isfile(tsv_concrete_name) or not os.path.isfile(additional_info_concrete_name):
            continue

        points_data = get_tiling.get_tags_data(tsv_concrete_name, additional_info_concrete_name)
        created_tilers[tiling_suffix] = get_tiling.LightTiler(points_data)

        functioning_names.append(tiling_name)
        print('Loaded {}.'.format(tiling_name))

    tiling_names = sorted(functioning_names)


@app.route('/search/<suffix>/<name>')
def search(suffix, name):
    if suffix not in created_tilers:
        return ''

    tiler = created_tilers[suffix]
    return ' '.join(map(str, tiler.search(name)))


@app.route('/get_tile_variants')
def tile_variants():
    return '<br>'.join(tiling_names)


@app.route('/tiles_<suffix>/<int:x>_<int:y>_<int:z>.png')
def serve_tile(suffix, x, y, z):
    if suffix not in created_tilers:
        return ""

    return send_from_directory('', 'tiles_{}/{}_{}_{}.png'.format(suffix, x, y, z))


@app.route('/')
def show_visualization():
    return send_from_directory('', 'tiling_visualizer.html')
