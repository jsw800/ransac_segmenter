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
type_of_test = sys.argv[4]

files = [join(json_dir, flnm) for flnm in os.listdir(json_dir) if 'json' in flnm]
shuffle(files)
for flnm in files:
    imgnum = flnm.split('/')[-1].split('.')[0]
    with open(flnm) as f:
        elements = json.load(f)
    in_img_path = (imgs_path + imgnum + '.jpg')
    img = cv2.imread(in_img_path)

    if type_of_test == 'points':
        try:
            for (x, y) in elements['corners']:
                img[int(y)-5:int(y)+6, int(x)-5:int(x)+6] = (0, 255, 0)
        except KeyError:
            print("Key Error: reading " + flnm)

    if type_of_test == 'ranges':
        try:
            for cell in elements['corners']:
                red = randint(0, 255)
                green = randint(0, 255)
                blue = randint(0, 255)
                img[cell[2]:cell[3], cell[0]:cell[1]] = (red, green, blue)
        except KeyError:
            print("Key Error: reading " + flnm)

    out_img_path = out_dir + 'test_' + imgnum + '.jpg'
    cv2.imwrite(out_img_path, img)
