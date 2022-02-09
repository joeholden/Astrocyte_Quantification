import matplotlib
import PIL
from PIL import Image
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
import pandas as pd
import math
import image_slicer
import os
import time

# To run this program, set up the following folders in the directory you are running this program from:
# [Area_Excel, binaries, histograms, mask_tiles, masks, recolored_tiles, stitched_binaries, tiles]
# Add static variable declarations for cython to increase speed!

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
    """Recolors each tile based on its binary image white density.
    Also returns total count of white pixels in binary image"""
    im = Image.open(image_path)
    # mode 'L' is greyscale. We want RGB because we have a binary image + a colored ROI -> 8bit
    # if im.mode == 'L':
    #     im = im.convert('RGB')
    im = im.convert('RGB')
    height, width = im.size

    if set(im.getdata()) != {(0, 0, 0)}:
        # pixel counts
        count_1 = 0
        count_0 = 0

        # loading a copy pixel map to manipulate and a reference to copy from
        pixel_map = im.load()
        img = Image.new(im.mode, im.size)
        pixels_new = img.load()

        # Count the white and black pixels.

        for i in range(im.width):
            for j in range(im.height):
                px = im.getpixel((i, j))
                if px == (255, 255, 255):
                    count_1 += 1
                else:
                    count_0 += 1
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

        try:
            area_fractions.append(round(count_1 / tile_area_list[tile_position], 2))
            full_area_fractions_for_zip.append(round(count_1 / tile_area_list[tile_position], 2))
        #     The full area fractions for zip variable is a list that is identical
        # to area fractions list but also contains zeros. Useful for keeping track of the tiles name.
        # You could re-write it to make area_fractions a list of tuples containing the tile_id.
        except ZeroDivisionError:
            area_fractions.append(0)
            full_area_fractions_for_zip.append(0)

    else:
        full_area_fractions_for_zip.append(0)
        im.save(f'recolored_tiles/{image_path.split("/")[1]}')
        count_1 = 0
    return count_1


def re_stitch():
    """Stitches all the density-recolored images together into a final image"""
    stitched_image = Image.new('RGB', (large_image.width, large_image.height))
    image_list = os.listdir('recolored_tiles')
    current_tile = 0

    for y in range(0, large_image.height - tile_dims[0] + 1, tile_dims[0]):
        for x in range(0, large_image.width - tile_dims[1] + 1, tile_dims[1]):

            try:
                tile_image = Image.open(f'recolored_tiles/{image_list[current_tile]}')
            except Exception as e:
                print(e)

            stitched_image.paste(tile_image, (x, y), 0)
            current_tile += 1

    stitched_image.save(f'stitched_{IMAGE_PATH}')
    print('Finished Stitching Image')


def make_histogram(file_name):
    """Makes a histogram plotting the frequency of each non-zero density tile"""
    fig, ax = plt.subplots(figsize=(14, 8), dpi=100)
    font = {'fontname': 'Arial'}

    plt.hist(area_fractions, bins=34, color='#6d1b7b', alpha=1)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.spines['left'].set_visible(True)

    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(1.5)

    ax.tick_params(width=2, length=7)
    plt.xticks(fontsize=18)
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.tick_params(axis='both', which='minor', labelsize=18)

    plt.xlim(-0.02, 1)
    if 'gfap' in file_name.lower():
        plt.xlabel('Density of GFAP', fontsize=24, **font)
        plt.ylabel('Normalized Frequency', fontsize=24, **font)
        plt.title('Distribution of Retinal GFAP Density', fontsize=36, **font)
    else:
        plt.xlabel('Density of Connexin 43', fontsize=24, **font)
        plt.ylabel('Normalized Frequency', fontsize=24, **font)
        plt.title('Distribution of Retinal Cx43 Density', fontsize=36, **font)

    plt.savefig(f'histograms/{b}')
    print('Finished Making Histogram')


def mask_roi_area():
    """Splits the mask into the same tile grid as the full image.
    Determines the fraction of each tile that is white and uses
    that as the area in the density calculations"""

    mask = Image.open(MASK_PATH)
    if mask.mode != 'L':
        mask.convert('L')
    split_grid(directory='mask_tiles', full_image_path=MASK_PATH)

    global tile_area_list, total_white_mask_area
    tile_area_list = []
    total_white_mask_area = 0

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
            total_white_mask_area += white_area
        print('', end='\r')
        print(t + ' mask area complete', end='\t')
    print('', end='\r')
    print('Finished getting mask area')


def make_background_transparent():
    """Makes any pixel that is black transparent. Likely not used in final program"""
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
    df_2 = pd.Series(full_area_fractions_for_zip)
    df.to_excel(f'Area_Excel/{b.strip(".png")}_Area_Fractions.xlsx')
    df_2.to_excel(f'Area_Excel/{b.strip(".png")}_Area_Fractions_With_Zeros.xlsx')


def clean_up():
    """Deletes all the temporary files created so there are no
    runtime problems with the next image if it is a different size"""

    for file in os.listdir('tiles'):
        os.remove(f'tiles/{file}')
    for file_ in os.listdir('recolored_tiles'):
        os.remove(f'recolored_tiles/{file_}')
    for file__ in os.listdir('mask_tiles'):
        os.remove(f'mask_tiles/{file__}')


def batch():
    """Runs all your image files in batch through the program defined by the rest of the project functions.
    This function itself contains the instructions to run the program"""
    global b, m
    list_of_image_paths = sorted(os.listdir('binaries'))
    list_of_mask_paths = sorted(os.listdir('masks'))
    file_groups = zip(list_of_image_paths, list_of_mask_paths)

    for (b, m) in file_groups:
        global IMAGE_PATH, MASK_PATH, my_colormap, large_image, i_width, i_height, num_rows, num_cols, area_fractions, full_area_fractions_for_zip
        IMAGE_PATH = f'binaries/{b}'
        MASK_PATH = f'masks/{m}'

        my_colormap = plt.get_cmap('inferno')
        PIL.Image.MAX_IMAGE_PIXELS = 9999999999

        large_image = Image.open(IMAGE_PATH)
        i_width, i_height = large_image.size
        # ~1000x1000 px tiles
        num_rows = math.ceil(i_height / 1000)
        num_cols = math.ceil(i_width / 1000)
        # num_rows = 30
        # num_cols = 30

        area_fractions = []
        full_area_fractions_for_zip = []

        start_time = time.time()

        split_grid(directory='tiles', full_image_path=IMAGE_PATH)
        mask_roi_area()

        step = 0
        white_count_in_binary_image = 0

        for tile in os.listdir('tiles'):
            out = get_binary_density_and_recolor(image_path=f'tiles/{tile}', tile_position=step)
            white_count_in_binary_image += out
            step += 1
            print('', end='\r')
            print(str(step) + ' recolored', end='\t')
        print('', end='\r')
        print('Finished Calculating Densities and Coloring Tiles')

        re_stitch()
        make_histogram(file_name=IMAGE_PATH)
        log_densities()
        clean_up()

        with open(f'white_pixels.txt', 'a') as txt_file:
            txt_file.write(f'{b.strip(".png")}\nWhite Area in Binary: {white_count_in_binary_image}, '
                           f'White Area in Mask {total_white_mask_area}\n')

        print("--- %s seconds ---" % round((time.time() - start_time), 3))


folders = ['Area_Excel', 'binaries', 'histograms', 'mask_tiles', 'masks', 'recolored_tiles',
           'stitched_binaries', 'tiles']
for n in range(len(folders)):
    isExist = os.path.exists(folders[n])
    if not isExist:
        os.mkdir(folders[n])

batch()
