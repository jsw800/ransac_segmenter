import cv2
import numpy as np
from os.path import join
import os
import random
import json
import sys
import utils

"""
For efficency, we downsample the images by 4. This speeds up SIFT and reduces the
number of SIFT features to match, as putative matching is a bottleneck in this process.
Feel free to change the downsample factor as needed. A smaller downsample factor will result
in a slower, more accurate segmentation. A larger downsample factor will speed things up, but
could reduce accuracy.
This factor was chosen for segmentation of the 1930 census. Depending on the resolution of
your images, this factor may or may not work for you.
"""

DOWNSAMPLE_FACTOR = 4

class RANSAC_segmenter:
    
    def __init__(self, template_img_path, template_points_path):
        self.template_img = cv2.imread(template_img_path)[::DOWNSAMPLE_FACTOR, ::DOWNSAMPLE_FACTOR]
        with open(template_points_path) as f:
            self.template_points = json.load(f)['corners']
        self.sift = cv2.xfeatures2d.SIFT_create()
        self.template_kp, self.template_descriptors = self.sift.detectAndCompute(self.template_img, None)

    # returns a list of corner points on the sample image
    def segment(self, sample_image):
        old_sample_image = sample_image
        sample_image = sample_image[::DOWNSAMPLE_FACTOR, ::DOWNSAMPLE_FACTOR]
        # get putative matches
        sample_kp, sample_descriptors = self.sift.detectAndCompute(sample_image, None)
        putative_matches = utils.get_putative_matches(sample_kp, sample_descriptors, self.template_kp, self.template_descriptors)

        # we probably can't actually segment if we have so few putative matches
        if len(putative_matches) < 100:
            return None

        # random sample putative matches 200 times to find best homography
        # homography maps sample to template
        EPS = 3
        bestc = 0
        best = None
        for i in range(200):
            # choose 4 random matches and calculate the homography
            random.shuffle(putative_matches)
            points1 = [match[0] for match in putative_matches[:4]]
            points2 = [match[1] for match in putative_matches[:4]]
            h = utils.find_homography(points1, points2)
            # h is none when 3 points are colinear
            if h is None:
                continue
            # see how many matches fall close (within EPS) to where they should
            good = 0
            for match in putative_matches:
                pointa = np.ones(3, dtype=np.float64)
                pointb = np.ones(3, dtype=np.float64)
                pointa[:2] = np.array(match[0])
                pointb[:2] = np.array(match[1])
                actual_b = h.dot(pointa)
                if actual_b[2] == 0:
                    continue
                actual_b /= float(actual_b[2])
                if np.linalg.norm(actual_b - pointb) < EPS:
                    good += 1
            if good > bestc:
                bestc = good
                best = h
        
        # if less than 50 points fell where they should, segmentation almost definitely failed.
        if bestc < 50:
            return None
        # invert because h is sample to template, we want template to sample
        h = best
        # TODO: possible although very unlikely infinite recursion
        # Possible fix: compute homography from template to sample and then we don't
        # have to invert and this retry recursion doesn't need to happen.
        try:
            h = np.linalg.inv(h)
        except np.linalg.LinAlgError as e:
            print('singular matrix, trying again')
            return self.segment(old_sample_image)
        h /= h[2,2]
        # now we have the best homography, we multiply it by all the template points.
        pts = np.ones((3, len(self.template_points)))
        for i in range(len(self.template_points)):
            pts[:2, i] = np.array([self.template_points[i][0], self.template_points[i][1]]) / DOWNSAMPLE_FACTOR
            pts[:, i] = np.matmul(h, pts[:, i])
            pts[:, i] /= pts[:, i][2]
        pts *= DOWNSAMPLE_FACTOR
        # if we get any negative values on a point, the segmentation probably failed.
        if np.min(pts) < 0:
            return None
        return pts[:2].astype(np.int32)


# main method will segment an entire folder of images.
if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('usage: python segmenter.py [template_img_path] [template_points_path] [sample_directory] [out_directory]')
        exit()
    template_img = sys.argv[1]
    template_points = sys.argv[2]
    sample_dir = sys.argv[3]
    out_dir = sys.argv[4]
    segmenter = RANSAC_segmenter(template_img, template_points)
    images = [join(sample_dir, flnm) for flnm in os.listdir(sample_dir) if 'jpg' in flnm]
    for flnm in images:
        imgnum = flnm.split('/')[-1].split('.')[0]
        sample_image = cv2.imread(flnm)
        points = segmenter.segment(sample_image)
        if points is None:
            print('could not segment ' + flnm)
            # if we couldn't segment, just write an empty json object to outfile.
            with open(join(out_dir, imgnum + '.json'), 'w+') as f:
                f.write('{}')
            continue
        out = [[int(points[:, i][0]), int(points[:, i][1])] for i in range(points.shape[1])]
        out = {'corners': out}
        with open(join(out_dir, imgnum + '.json'), 'w+') as f:
            print('segmented ' + flnm)
            f.write(json.dumps(out))

