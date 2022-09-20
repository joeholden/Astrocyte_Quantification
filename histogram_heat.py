import cv2
import matplotlib.pyplot as plt
import math
from collections import defaultdict
from speed_up import split_image_for_multiprocessing
import multiprocessing as mp
import concurrent.futures
import time

BINARY_PATH = 'binary2.png'
HEATMAP_PATH = 'reconstructed.png'
plt.style.use('ggplot')
BIN_NUMBER = 16 # Use 16 bins ~sqrt(255)
COLOR = "#4d0f4d"


def histogram(width_bounds, height_bounds):
    binary = cv2.imread(BINARY_PATH, cv2.IMREAD_GRAYSCALE)
    retina_coordinates = []
    for x in range(width_bounds[0], width_bounds[1]):
        for y in range(height_bounds[0], height_bounds[1]):
            if binary[y,x] == 255:
                retina_coordinates.append((x, y))

    im = cv2.imread(HEATMAP_PATH, cv2.IMREAD_GRAYSCALE)
    intensity_list = []
    for x, y in retina_coordinates:
        intensity_list.append(im[y, x])
    return intensity_list



if __name__ == '__main__':
    start = time.time()
    dictionary = split_image_for_multiprocessing(HEATMAP_PATH)

    # Try with ProcessPoolExecutor and ThreadPoolExecutor for speed changes
    # multithreading is faster than multiprocessing in this case
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for core in range(mp.cpu_count()):
            data = dictionary[f'image_{core}']
            f = executor.submit(histogram, (data[2], data[3]), (data[0], data[1]))
            futures.append(f)

        merged_intensities = []
        for f in concurrent.futures.as_completed(futures):
            for p in f.result():
                merged_intensities.append(p)

        plt.figure(figsize=(8, 6))
        plt.hist(merged_intensities, bins=BIN_NUMBER, color=COLOR)
        plt.title('Heatmap Intensities', fontsize=22)
        plt.xlabel('8-bit Intensity', fontsize=16)
        plt.ylabel('Frequency', fontsize=16)
        end = time.time()
        print(f"Executed in {round(end - start, 3)} seconds")
        plt.show()
