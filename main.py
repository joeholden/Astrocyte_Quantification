import PIL
import matplotlib
from PIL import Image
from matplotlib.colors import LinearSegmentedColormap
import math
import image_slicer
import os

my_colors = ['#fde725', '#9fda3a', '#4ac26e', '#1fa187', '#27a187', '#365c8d', '#47327f', '#440154']
my_colormap = LinearSegmentedColormap.from_list('my_colormap', my_colors, N=500)

IMAGE_PATH = 'binary.png'
PIL.Image.MAX_IMAGE_PIXELS = 9999999999

large_image = Image.open(IMAGE_PATH)
i_width, i_height = large_image.size
# ~1000x1000 px tiles
num_rows = math.ceil(i_height / 1000)
num_cols = math.ceil(i_width / 1000)


def split_grid(directory, full_image_path):
    tiles = image_slicer.slice(full_image_path, num_rows * num_cols, save=False)
    image_slicer.save_tiles(tiles, directory=directory, prefix='slice', format='png')
    sample_tile_file = os.listdir('tiles')[0]
    sample_tile = Image.open(f'tiles/{sample_tile_file}')
    global tile_dims
    tile_dims = (sample_tile.height, sample_tile.width)


def get_binary_density_and_recolor(image_path, tile_position):
    im = Image.open(image_path)
    # mode 'L' is greyscale. We want RGB because we have a binary image + a colored ROI -> 8bit
    if im.mode == 'L':
        im = im.convert('RGB')
    height, width = im.size

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


def re_stitch():
    stitched_image = Image.new('RGB', (large_image.width, large_image.height))
    image_list = os.listdir('recolored_tiles')
    current_tile = 0

    for y in range(0, large_image.height - 1, tile_dims[0]):
        for x in range(0, large_image.width - 1, tile_dims[1]):
            tile_image = Image.open(f'recolored_tiles/{image_list[current_tile]}')
            stitched_image.paste(tile_image, (x, y), 0)
            current_tile += 1

    stitched_image.save(f'stitched_{IMAGE_PATH}.png')


def make_histogram():
    pass


def mask_roi_area():
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
    print('done getting mask area')


# ///////////Program/////////////
split_grid(directory='tiles', full_image_path=IMAGE_PATH)
mask_roi_area()

step = 0
for tile in os.listdir('tiles'):
    get_binary_density_and_recolor(image_path=f'tiles/{tile}', tile_position=step)
    step += 1
    print(step)

re_stitch()
make_histogram()



