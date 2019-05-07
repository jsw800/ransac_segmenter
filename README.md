# ransac_segmenter

This repository implements tabular segmentation using SIFT features and RANSAC.
It relies on a single template image with labeled corner points. This image must contain
a document formatted in exactly the same way as the samples to be segmented.
RANSAC will generate a homography that will transform the template points onto each
sample image using a projective transformation.

We provide a template image and points for the 1930 census in the data/ directory.

# Details

## SIFT

We utilize SIFT, which locates interest points in an image and gives 128-dimensional
descriptors of those interest points. Descriptors in one image that are very close to
descriptors in another image are likely the same point (or in our case, correspond to the
same place in an image of a table).

## Putative matches
We want to identify interest points between the template and sample images that "match".
In order to do this robustly, we choose only matches that are "putative", that is, the
template descriptor and sample descriptor both "choose" each other as the closest descriptor
in the other image. We also only consider putative matches that are confident in their "choice"
of match. In other words, if a putative match's "second choice" is more than 0.75 times the
distance from it's first choice, we do not consider this match, as it is not a confident match.
A putative match consists of 2 (x, y) points, one on the template image, one on the sample image.

## RANSAC
RANSAC stands for Random SAmple with Consensus. In our context, we randomly sample 4 putative
matches and use these matches to compute a homography. We want this homography to transform the
sample image onto the template image. Once we have a homography, we use it to transform the sample
point from each putative match, and then we test if it falls close to its match in the template
image. We count how many of the sample points transform onto their match in the template image.
We repeat this process 200 times, randomly sampling 4 matches and computing homographies,
and we keep the homography that transforms the most sample points onto their putative matches.
This process allows us to use consensus to prune out putative matches that are spurious and
find a transformation that takes only the non-spurious putative matches into account.

## Transformation
After RANSAC, we have a homography matrix that transforms points on the sample image to
points on the template image. In order to transfer the labels from the template image onto
the sample image, we invert the RANSAC homography, and multiply this inverse by each point
from the template labels (normalizing them in homogeneous coordinates). The points we get out
should correspond to the table corner points on the sample image, and we are done.
