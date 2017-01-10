# -*- coding: utf-8 -*-
import csv
import os
import click
import logging
import numpy as np

from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler


@click.command()
@click.argument('tsne_positions_file_name')
@click.argument('tags_additional_info_file_name')
def main(tsne_positions_file_name, tags_additional_info_file_name):
    tag_positions = []
    with  open(tsne_positions_file_name) as tag_positions_file:
        for line in tag_positions_file.readlines()[1:]:
            words = line.strip().split('\t')
            tag_positions.append((float(words[0]), float(words[1])))
    tag_positions = np.array(tag_positions)
    # tag_distances = np.memmap('data/interim/pairwise_dist_map.memmap', dtype='float32', mode='w+', shape=(200000, 1000))

    db = DBSCAN(eps=0.6, min_samples=10).fit(tag_positions)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    tags_info = []
    tags_info_field_names = []
    with open(tags_additional_info_file_name) as tags_info_file:
        tags_info_reader = csv.DictReader(tags_info_file)
        tags_info_field_names = list(tags_info_reader.fieldnames)
        if 'cluster_label' not in tags_info_field_names:
            tags_info_field_names.append('cluster_label')

        for cluster_label, other_info in zip(labels, tags_info_reader):
            other_info['cluster_label'] = cluster_label
            tags_info.append(other_info)

    cluster_names = {}
    for tag_info in tags_info:
        cluster_label = tag_info['cluster_label']
        tag_name = tag_info['name']
        number_of_posts = int(tag_info['PostCount'])
        if cluster_label not in cluster_names:
            cluster_names[cluster_label] = (tag_name, number_of_posts)
        else:
            # selecting tag with most posts as cluster name, if two tags have same number of posts we select tag
            # with shorter name
            if (cluster_names[cluster_label][1] < number_of_posts or
                    (cluster_names[cluster_label][1] == number_of_posts and
                             len(cluster_names[cluster_label][0]) > len(tag_name))):
                cluster_names[cluster_label] = (tag_name, number_of_posts)

    # adding cluster names to data
    if 'cluster_name' not in tags_info_field_names:
        tags_info_field_names.append('cluster_name')
    for tag_info in tags_info:
        tag_info['cluster_name'] = cluster_names[tag_info['cluster_label']][0]


    with open(tags_additional_info_file_name, 'w') as tags_info_file:
        tags_info_writer = csv.DictWriter(tags_info_file, tags_info_field_names)
        tags_info_writer.writeheader()
        tags_info_writer.writerows(tags_info)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # often useful for finding various files
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables


    main()
