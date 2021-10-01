import PIL
import matplotlib
from PIL import Image
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
import pandas as pd
import math
import image_slicer
import os
import time

my_colormap = plt.get_cmap('inferno')

IMAGE_PATH = 'binary.png'
PIL.Image.MAX_IMAGE_PIXELS = 9999999999

large_image = Image.open(IMAGE_PATH)
i_width, i_height = large_image.size
# ~1000x1000 px tiles
num_rows = math.ceil(i_height / 1000)
num_cols = math.ceil(i_width / 1000)
area_fractions = []


def split_grid(directory, full_image_path):
    """Splits the image into a grid of tiles ~1000x1000 px^2"""
    tiles = image_slicer.slice(full_image_path, num_rows * num_cols, save=False)
    image_slicer.save_tiles(tiles, directory=directory, prefix='slice', format='png')
    sample_tile_file = os.listdir('tiles')[0]
    sample_tile = Image.open(f'tiles/{sample_tile_file}')
    global tile_dims
    tile_dims = (sample_tile.height, sample_tile.width)
    print(f'Finished Splitting Grid From: {full_image_path}')


def get_binary_density_and_recolor(image_path, tile_position):
    """Recolors each tile based on its binary image white density"""
    im = Image.open(image_path)
    # mode 'L' is greyscale. We want RGB because we have a binary image + a colored ROI -> 8bit
    if im.mode == 'L':
        im = im.convert('RGB')
    height, width = im.size

    if set(im.getdata()) != {(0, 0, 0)}:
        # pixel counts
        count_1 = 0
        count_0 = 0
        count_red = 0

        # loading a copy pixel map to manipulate and a reference to copy from
        pixel_map = im.load()
        img = Image.new(im.mode, im.size)
        pixels_new = img.load()

        # Count the white, black, and non-binary pixels.
        # ImageJ ROIs are not one color if made on a diagonal.
        for i in range(im.width):
            for j in range(im.height):
                px = im.getpixel((i, j))
                if px == (255, 255, 255):
                    count_1 += 1
                elif px == (0, 0, 0):
                    count_0 += 1
                else:
                    count_red += 1
        try:
            normalized_area = (500 * count_1) / tile_area_list[tile_position]
        except ZeroDivisionError:
            normalized_area = (500 * count_1) / (tile_dims[0] * tile_dims[1])

        # extracts the color corresponding to each value 1-500 in the colormap.
        cmap_color_hex = matplotlib.colors.rgb2hex(my_colormap(round(normalized_area)))
        cmap_color_rgb = tuple(int(cmap_color_hex.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))

        for k in range(im.width):
            for l in range(im.height):
                if pixel_map[k, l] == (255, 255, 255):
                    pixels_new[k, l] = cmap_color_rgb
                elif pixel_map[k, l] != (0, 0, 0):
                    pixels_new[k, l] = (0, 0, 0)
                else:
                    pixels_new[k, l] = pixel_map[k, l]
        img.save(f'recolored_tiles/{image_path.split("/")[1]}')
        if count_1 > 0:
            area_fractions.append(round(count_1 / tile_area_list[tile_position], 2))
    else:
        im.save(f'recolored_tiles/{image_path.split("/")[1]}')


def re_stitch():
    """Stitches all the density-recolored images together into a final image"""
    stitched_image = Image.new('RGB', (large_image.width, large_image.height))
    image_list = os.listdir('recolored_tiles')
    current_tile = 0

    for y in range(0, large_image.height - tile_dims[0] + 1, tile_dims[0]):
        for x in range(0, large_image.width - tile_dims[1] + 1, tile_dims[1]):
            # Fix this shit
            try:
                tile_image = Image.open(f'recolored_tiles/{image_list[current_tile]}')
            except:
                pass
            stitched_image.paste(tile_image, (x, y), 0)
            current_tile += 1

    stitched_image.save(f'stitched_{IMAGE_PATH}.png')
    print('Finished Stitching Image')


def make_histogram():
    """Makes a histogram plotting the frequency of each non-zero density tile"""
    fig = plt.figure(dpi=300)
    plt.hist(area_fractions, bins=50)
    plt.title('Frequency Distribution of Astrocyte Densities in Local Retina Regions')
    plt.xlabel('GFAP Tile Density')
    plt.ylabel('Frequency')
    plt.savefig('histogram.png')
    print('Finished Making Histogram')


def mask_roi_area():
    """Splits the mask into the same tile grid as the full image.
    Determines the fraction of each tile that is white and uses
    that as the area in the density calculations"""

    mask = Image.open('mask.png')
    if mask.mode != 'L':
        mask.convert('L')
    split_grid(directory='mask_tiles', full_image_path='mask.png')

    global tile_area_list
    tile_area_list = []

    for t in os.listdir('mask_tiles'):
        area_tile = Image.open(f'mask_tiles/{t}')
        area_tile_dims = (area_tile.height, area_tile.width)
        if set(area_tile.getdata()) == {0}:
            tile_area_list.append(0)
        else:
            white_area = 0
            for q in range(area_tile_dims[1]):
                for r in range(area_tile_dims[0]):
                    px = area_tile.getpixel((q, r))
                    if px != 0:
                        white_area += 1
            tile_area_list.append(white_area)
        print('', end='\r')
        print(t + ' mask area complete', end='\t')
    print('', end='\r')
    print('Finished getting mask area')


def make_background_transparent():
    """Makes any pixel that is black transparent"""
    im = Image.open('stitched_binary thresholded.tif.png')
    im = im.convert('RGBA')
    pixel_map_t = im.load()
    img_t = Image.new(im.mode, im.size)
    pixels_new_t = img_t.load()

    for m in range(im.width):
        for n in range(im.height):
            if pixel_map_t[m, n] == (0, 0, 0, 255):
                pixels_new_t[m, n] = (0, 0, 0, 0)
            else:
                pixels_new_t[m, n] = pixel_map_t[m, n]
    img_t.save('transparent.png')
    print('Done Making Background Transparent')


def log_densities():
    """Creates a simple excel sheet with a single column of the tile GFAP densities"""
    df = pd.Series(area_fractions)
    df.to_excel(f'Area_Fractions.xlsx')


def clean_up():
    """Deletes all the temporary files created so there are no
    runtime problems with the next image if it is a different size"""

    for file in os.listdir('tiles'):
        os.remove(f'tiles/{file}')
    for file_ in os.listdir('recolored_tiles'):
        os.remove(f'recolored_tiles/{file_}')
    for file__ in os.listdir('mask_tiles'):
        os.remove(f'mask_tiles/{file__}')


# ///////////////////////////////////////////////Program////////////////////////////////////////////////////////////////
start_time = time.time()

split_grid(directory='tiles', full_image_path=IMAGE_PATH)
mask_roi_area()

step = 0
for tile in os.listdir('tiles'):
    get_binary_density_and_recolor(image_path=f'tiles/{tile}', tile_position=step)
    step += 1
    print('', end='\r')
    print(str(step) + ' recolored', end='\t')
print('', end='\r')
print('Finished Calculating Densities and Coloring Tiles')

re_stitch()
make_histogram()
log_densities()
clean_up()

print("--- %s seconds ---" % round((time.time() - start_time), 3))

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


