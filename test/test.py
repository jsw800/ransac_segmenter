import cv2
import numpy as np
from os.path import join
import os
import random
import json
import sys
from random import shuffle
from random import randint


DOWNSAMPLE_FACTOR = 4

imgs_path = sys.argv[1]
json_dir = sys.argv[2]
out_dir = sys.argv[3]

ranges = [join(json_dir, flnm) for flnm in os.listdir(json_dir) if 'json' in flnm]
shuffle(ranges)
for flnm in ranges:
    imgnum = flnm.split('/')[-1].split('.')[0]
    with open(flnm) as f:
        cells = json.load(f)
    in_img_path = (imgs_path + imgnum + '.jpg')
    img = cv2.imread(in_img_path)
    try:
        for cell in cells['corners']:
            red = randint(0, 255)
            green = randint(0, 255)
            blue = randint(0, 255)
            img[cell[2]:cell[3], cell[0]:cell[1]] = (red, green, blue)
    except KeyError:
        print("Key Error: reading " + flnm)
    out_img_path = out_dir + 'test_' + imgnum + '.jpg'
    cv2.imwrite(out_img_path, img)
