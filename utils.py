import numpy as np
import cv2


# 4 point algorithm
# p1, p2 are lists of 4 (x, y) points
def find_homography(p1, p2):
    A = np.matrix([[p1[0][0], p1[0][1], 1, 0, 0, 0, -p2[0][0]*p1[0][0], -p2[0][0]*p1[0][1]],
                  [0, 0, 0, p1[0][0], p1[0][1], 1, -p2[0][1]*p1[0][0], -p2[0][1]*p1[0][1]],
                  [p1[1][0], p1[1][1], 1, 0, 0, 0, -p2[1][0]*p1[1][0], -p2[1][0]*p1[1][1]],
                  [0, 0, 0, p1[1][0], p1[1][1], 1, -p2[1][1]*p1[1][0], -p2[1][1]*p1[1][1]],
                  [p1[2][0], p1[2][1], 1, 0, 0, 0, -p2[2][0]*p1[2][0], -p2[2][0]*p1[2][1]],
                  [0, 0, 0, p1[2][0], p1[2][1], 1, -p2[2][1]*p1[2][0], -p2[2][1]*p1[2][1]],
                  [p1[3][0], p1[3][1], 1, 0, 0, 0, -p2[3][0]*p1[3][0], -p2[3][0]*p1[3][1]],
                  [0, 0, 0, p1[3][0], p1[3][1], 1, -p2[3][1]*p1[3][0], -p2[3][1]*p1[3][1]]])
    y = np.matrix([[p2[0][0]],
                  [p2[0][1]],
                  [p2[1][0]],
                  [p2[1][1]],
                  [p2[2][0]],
                  [p2[2][1]],
                  [p2[3][0]],
                  [p2[3][1]]])
    try:
        h = np.linalg.solve(A, y)
    # this exception happens only when 3 points in either p1 or p2 are colinear
    except:
        return None
    retval = np.zeros([3,3], dtype=np.float64)
    c = 0
    for i in range(3):
        for j in range(3):
            if i==2 and j==2:
                retval[i, j] = 1
            else:
                retval[i, j] = h[c]
            c += 1
    return retval


"""
given SIFT keypoints and descriptors for each image, return pairs of points that are
likely the same point in the two images
"""
def get_putative_matches(kp1, des1, kp2, des2):
    # use cv2 to calculate the matches
    matcher = cv2.BFMatcher()
    matches = matcher.knnMatch(des1, des2, k=2)
    retval = []
    # prune out matches that are not confident enough,
    # and put matches into tuples of ((x1, y1), (x2, y2))
    for i, pair in enumerate(matches):
        if float(pair[0].distance) / float(pair[1].distance) > 0.75:
            continue
        frm = kp1[pair[0].queryIdx].pt
        frm = (int(frm[0]), int(frm[1]))
        to = kp2[pair[0].trainIdx].pt
        to = (int(to[0]), int(to[1]))
        retval.append((frm, to))
    return retval
