from itertools import groupby

import cv2
import numpy as np

from phenotyping_segmentation.traits.skeleton import get_root_info


def get_seed(pts, hull=None):
    """Get root system seed location.

    Args:
        pts: Points used to compute the convex hull.
        hull: ConvexHull object.

    Returns:
        x and y locations of seed.
    """
    if len(pts) == 0:
        return np.nan, np.nan
    # get cv2 convex hull
    if not hull:
        convexhull = np.squeeze(cv2.convexHull(pts), axis=1)
    # order from top to bottom, starting from the top one
    convexhull_start = convexhull.copy()[np.lexsort(convexhull.copy().T)]
    starty = convexhull_start[0][1]
    startx = np.mean(
        convexhull[np.argwhere(convexhull[:, 1] == starty), 0], dtype=np.int64
    )
    return startx, starty


def get_scanline_intersects(img, y):
    """Get the scanline root counts and angle at this scanline.

    Args:
        img: image
        y: y location of scanline

    Returns:
        root counts and width at this scanline, left and right root locations.
    """
    img_y = img[y, :]
    clusters_y = [
        sum(1 for _ in group) for key, group in groupby(img_y) if key == 255
    ]  # get the root count
    root_count = len(clusters_y)

    # get the left and right root at the scanline
    non_zero_indices = list(np.nonzero(img_y)[0])
    if non_zero_indices:
        left = non_zero_indices[0]
        right = non_zero_indices[-1]
        width = abs(right - left)
    else:
        root_count = np.nan
        left = np.nan
        right = np.nan
        width = np.nan
    return root_count, width, left, right
