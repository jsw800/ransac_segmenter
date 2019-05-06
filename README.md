# ransac_segmenter

This repository implements tabular segmentation using SIFT features and RANSAC.
It relies on a single template image with labeled corner points. This image must contain
a document formatted in exactly the same way as the samples to be segmented.
RANSAC will generate a homography that will transform the template points onto each
sample image using a projective transformation.
