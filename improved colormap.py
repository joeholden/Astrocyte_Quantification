import cv2
import matplotlib.cm as cm
import matplotlib as mpl
import matplotlib.pyplot as plt
import math

im = cv2.imread('gfap.png', cv2.IMREAD_UNCHANGED)


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
    color = [int(round(i*255, 0)) for i in color]
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

    x_bounds = (x-r, x+r)
    y_bounds = (y-r, y+r)

    pixels = []
    for i in range(x_bounds[0], x_bounds[1]):
        for j in range(y_bounds[0], y_bounds[1]):
            # im[j, i] = [0, 0, 0]
            pixels.append((i,j))
    return pixels


RADIUS = 9
heat_image = cv2.imread('gfap.png', cv2.IMREAD_UNCHANGED)
heat_image = cv2.cvtColor(heat_image, cv2.COLOR_GRAY2RGB)
# plot_image(image_object=heat_image, from_path=False)
height, width, channel = heat_image.shape
for x in range(width):
    for y in range(height):
        int_sum = 0
        px = get_pixels_in_rectangle((x, y), RADIUS)
        try:
            for p in px:
                px_rgb = im[p[1], p[0]]
                int_sum += px_rgb
        except IndexError:
            pass #found the image bounds
        rgb = return_rgb_for_colormap(lower_limit=0, upper_limit=256*(RADIUS**2), value_to_map=int_sum, mpl_colormap='viridis')
        # yOU NEED TO ACCOUNT FOR EDGE EFFECTS SO YOU DONT GET A PURPLE BAR AT THE BOTTOM OF THE IMAGE
        heat_image[y,x] = rgb

plot_image(image_object=heat_image, from_path=False)
cv2.imwrite('test_recolor.png', heat_image)


