import cv2
import matplotlib.pyplot as plt
import math
import datetime
import multiprocessing as mp
from collections import defaultdict
import os
from pathlib import Path
import time
import concurrent.futures
import shutil


def plot_image(path=None, from_path=True, image_object=None, read_type=cv2.IMREAD_UNCHANGED):
    if from_path:
        im = cv2.imread(path, read_type)
        cv2.imshow('image', im)
        cv2.waitKey()
        cv2.destroyAllWindows()
    else:
        cv2.imshow('image', image_object)
        cv2.waitKey()
        cv2.destroyAllWindows()


def return_rgb_for_colormap(lower_limit, upper_limit, value_to_map, mpl_colormap):
    """The range of colormaps is always between 0 and 1. You will need to normalize your data to this range.
    This function maps the range between lower_limit and upper_limit linearly to the colors of mpl_colormap.
    This returns an 8-bit depth RGB tuple"""

    cmap = plt.get_cmap(mpl_colormap)
    norm = plt.Normalize(lower_limit, upper_limit)

    color = cmap(norm(value_to_map))
    color = [int(round(i * 255, 0)) for i in color]
    color = (color[0], color[1], color[2])
    return color


def rgb2bgr(rgb_tuple):
    bgr = (rgb_tuple[2], rgb_tuple[1], rgb_tuple[0])
    print(bgr)


def loop_through_pixels(image_object, function, f_param):
    # Change the following line... if its not rgb then there will not be a channel param
    height, width, channel = image_object.shape
    for x in range(width):
        for y in range(height):
            function(f_param)


def get_pixels_in_rectangle(starting_point, radius):
    x = starting_point[0]
    y = starting_point[1]
    r = radius

    x_bounds = (x - r, x + r)
    y_bounds = (y - r, y + r)

    pixels = []
    for i in range(x_bounds[0], x_bounds[1]):
        for j in range(y_bounds[0], y_bounds[1]):
            # im[j, i] = [0, 0, 0]
            pixels.append((i, j))
    return pixels


def split_image_for_multiprocessing(image_path):
    """returns a dictionary where values are a list containing the bounds in the original coordinate space
    and also the sliced image itself. [y_start, y_end, 0, image width]"""
    # leave one core open so the computer doesnt freeze everything else
    max_cores = mp.cpu_count() - 1
    im = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    height = im.shape[0]
    width = im.shape[1]
    slice_height = math.floor(height / max_cores)

    slice_bounds_and_image = defaultdict()
    y_start = 0
    y_end = slice_height
    for i in range(max_cores):
        slice_bounds_and_image[f'image_{i}'] = [y_start, y_end, 0, width, im[y_start:y_end, 0:width]]
        y_start = y_end
        y_end += slice_height
    return slice_bounds_and_image


def create_heatmap(image_path, width_bounds, height_bounds, radius, cmap):
    """provide bounds as a tuple
    7x speed increase over processing the whole image on one core for my machine"""
    RADIUS = radius
    im = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    heat_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    heat_image = cv2.cvtColor(heat_image, cv2.COLOR_GRAY2RGB)
    # Make the heat image the horizontal slice
    heat_image = heat_image[height_bounds[0]:height_bounds[1], width_bounds[0]:width_bounds[1]]

    for x in range(width_bounds[0], width_bounds[1]):
        for y in range(height_bounds[0], height_bounds[1]):
            int_sum = 0
            px = get_pixels_in_rectangle((x, y), RADIUS)
            num_px_out_of_range = 0
            try:
                for p in px:
                    px_rgb = im[p[1], p[0]]
                    int_sum += px_rgb
            except IndexError:
                num_px_out_of_range += 1
                pass  # found the image bounds
            rgb = return_rgb_for_colormap(lower_limit=0, upper_limit=256 * (RADIUS ** 2 - num_px_out_of_range),
                                          value_to_map=int_sum, mpl_colormap=cmap)
            # Account for edge effects because of purple bar at the bottom? num_px_out_of_range doesnt fix this
            heat_image[y - height_bounds[0], x] = rgb

    # plot_image(image_object=heat_image, from_path=False)
    Path('heat_slices').mkdir(parents=True, exist_ok=True)
    cv2.imwrite(f'heat_slices/heat_slice_{height_bounds[1]}.png', heat_image)


if __name__ == '__main__':
    start = time.time()
    RADIUS = 30
    IMAGE_PATH = '11_15/downsized binary.png'
    # If CMAP is not 'gray', the histogram x-span is reduced because of RGB to 8 bit conversion
    CMAP = 'gray'

    im = cv2.imread(IMAGE_PATH, cv2.IMREAD_UNCHANGED)
    dictionary = split_image_for_multiprocessing(IMAGE_PATH)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for core in range(mp.cpu_count()-1):
            data = dictionary[f'image_{core}']
            f = executor.submit(create_heatmap, IMAGE_PATH, (data[2], data[3]), (data[0], data[1]), RADIUS, CMAP)

    image_names = []
    for root, dirs, files in os.walk('heat_slices'):
        for file in files:
            if file.endswith('.png'):
                image_names.append(file)

    image_names = sorted([int(i.split('_')[-1].split('.')[0]) for i in image_names])
    image_names = [cv2.imread(os.path.join('heat_slices', 'heat_slice_' + str(i) + '.png')) for i in image_names]

    reconstruct = cv2.vconcat(image_names)

    Path('Reconstructed Images').mkdir(parents=True, exist_ok=True)
    try:
        cv2.imwrite(f'Reconstructed Images/{datetime.datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")}_Radius_{RADIUS}.png', reconstruct)
    except Exception as e:
        print(e)
    shutil.rmtree('heat_slices')
    stop = time.time()
    print(stop - start)
