# -*- coding: utf-8 -*-
import os
import logging
import numpy as np
from scipy import ndimage as ndi
import matplotlib.pyplot as plt
from skimage.feature import peak_local_max
from skimage import data, img_as_float


def point_to_image(point, points_bbox, image_size):
    px, py = point
    min_x, min_y, max_x, max_y = points_bbox
    im_w, im_h = image_size

    ix = int((px - min_x) / (max_x - min_x) * (im_w-1))
    iy = int((py - min_y) / (max_y - min_y) * (im_h-1))
    return ix, iy


def main():
    points = np.array([[float(w) for w in line.strip().split('\t')] for line in open(
        os.path.join(project_dir, 'data', 'processed', 'tsne_output_2008-01-01.tsv')).readlines()[1:] if
                       line.strip()])
    min_x, min_y, max_x, max_y = min(points[:, 0]), min(points[:, 1]), max(points[:, 0]), max(points[:, 1])
    points_bbox = (min_x, min_y, max_x, max_y)

    image_size = (1000, 1000)

    tags = [tuple( int(w) for w in line.strip().split(',')) for line in
            open(os.path.join(project_dir, 'data', 'interim', 'post_count_2008-01-01.csv')).readlines()[1:] if
            line.strip()]

    tag_names = {int(line.strip().split(',')[0]):line.strip().split(',')[1] for line in
            open(os.path.join(project_dir, 'data', 'interim', 'tags.csv')).readlines()[1:] if
            line.strip()}

    image = np.zeros(image_size)
    point_to_tag_id = {}
    for tag_numer, (tag_id, pos_count) in enumerate(tags):
        tag_on_image = point_to_image(points[tag_numer], points_bbox, image_size)
        point_to_tag_id[tag_on_image] = tag_id
        image[tag_on_image] = pos_count

    from scipy import ndimage as ndi
    import matplotlib.pyplot as plt
    from skimage.feature import peak_local_max
    from skimage import data, img_as_float

    im = image

    dilation_element_size = 100
    # image_max is the dilation of im with a 20*20 structuring element
    # It is used within peak_local_max function
    image_max = ndi.maximum_filter(im, size=dilation_element_size, mode='constant')

    # Comparison between image_max and im to find the coordinates of local maxima
    coordinates = peak_local_max(im, min_distance=dilation_element_size)
    for c in coordinates:
        print(tag_names[point_to_tag_id[tuple(c)]])
    print(len(coordinates))
    # display results
    fig, ax = plt.subplots(1, 3, figsize=(8, 3), sharex=True, sharey=True, subplot_kw={'adjustable': 'box-forced'})
    ax1, ax2, ax3 = ax.ravel()
    ax1.imshow(im, cmap=plt.cm.gray)
    ax1.axis('off')
    ax1.set_title('Original')

    ax2.imshow(image_max, cmap=plt.cm.gray)
    ax2.axis('off')
    ax2.set_title('Maximum filter')

    ax3.imshow(im, cmap=plt.cm.gray)
    ax3.autoscale(False)
    ax3.plot(coordinates[:, 1], coordinates[:, 0], 'r.')
    ax3.axis('off')
    ax3.set_title('Peak local max')

    fig.subplots_adjust(wspace=0.02, hspace=0.02, top=0.9,
                        bottom=0.02, left=0.02, right=0.98)

    plt.show()
    pass


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # often useful for finding various files
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables

    main()
