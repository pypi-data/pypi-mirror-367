import math

import cv2
import numpy as np


def conv_hull(pts):
    """Compute the convex hull for the points per frame.

    Args:
        pts: Root landmarks as an array of shape (..., 2).

    Returns:
        An object representing the convex hull or None if a hull can't be formed.
    """
    # Ensure the input is an array of shape (n, 2)
    if pts.ndim < 2 or pts.shape[-1] != 2:
        raise ValueError("Input points should be of shape (..., 2).")

    # Reshape and filter out NaN values
    pts = pts.reshape(-1, 2)
    pts = pts[~np.isnan(pts).any(axis=-1)]

    # Check for NaNs or infinite values
    if np.isnan(pts).any() or np.isinf(pts).any():
        return None, None, None

    # Ensure there are at least 3 unique non-collinear points
    if len(np.unique(pts, axis=0)) < 3:
        return None, None, None

    # Compute and return the convex hull
    hull = cv2.convexHull(pts)
    chull_area = cv2.contourArea(hull)
    chull_perimeter = cv2.arcLength(hull, True)  # True means closed contour

    return hull, chull_area, chull_perimeter


def get_angle_point(point, start):
    """Calculate the angle between a point and a start point.

    Args:
        point: Left or right point as an array of shape (2,).
        start: Start point as an array of shape (2,).

    Returns:
        The angle in degrees.
    """
    if len(point) > 0 and len(start) > 0:
        angle = abs(
            math.degrees((math.atan2(point[0] - start[0], point[1] - start[1])))
        )
    else:
        angle = np.nan
    return angle


def get_conv_angles(hull, pts, skeleton_img):
    """Get the angles of the convex hull edges.

    Args:
        hull: ConvexHull object.
        pts: Points used to compute the convex hull.
        skeleton_img: Skeleton image.

    Returns:
        Angles of the convex hull edges.
    """
    if hull is None:
        return (None,) * 9

    # get cv2 convex hull
    convexhull = np.squeeze(cv2.convexHull(pts), axis=1)

    # get start point (seed)
    # order from top to bottom, starting from the top one
    convexhull_start = convexhull.copy()[np.lexsort(convexhull.copy().T)]
    starty = convexhull_start[0][1]
    startx = np.mean(
        convexhull[np.argwhere(convexhull[:, 1] == starty), 0], dtype=np.int64
    )
    start = np.array([startx, starty])

    # get end point
    # order from top to bottom, starting from the bottom one
    endy = convexhull_start[-1][1]
    endx = np.mean(convexhull[np.argwhere(convexhull[:, 1] == endy), 0], dtype=np.int64)
    end = np.array([endx, endy])

    # order from left to right, starting from the left one
    # get the most left point and the most right point
    convexhull_most = convexhull.copy()[np.lexsort(convexhull.copy()[:, ::-1].T)]
    leftx = convexhull_most[0][0]
    lefty = np.mean(
        convexhull_most[np.argwhere(convexhull_most[:, 0] == leftx), 1], dtype=np.int64
    )
    left_most = np.array([leftx, lefty])
    rightx = convexhull_most[-1][0]
    righty = np.mean(
        convexhull_most[np.argwhere(convexhull_most[:, 0] == rightx), 1], dtype=np.int64
    )
    right_most = np.array([rightx, righty])

    # get top left and right points
    convexhull_img = np.zeros_like(skeleton_img, dtype=np.uint8)
    cv2.polylines(convexhull_img, [convexhull], True, 255, 1)

    convexhull_Contours = np.argwhere(convexhull_img == 255)[:, ::-1]
    left = convexhull_Contours[
        np.argwhere(convexhull_Contours[:, 0] < start[0]).squeeze()
    ]
    left_ = left[np.argwhere(left[:, 1] == start[1] + 10)]
    left_ = np.concatenate(
        (left_, left[np.argwhere(left[:, 1] == start[1] + 30)]), axis=0
    )
    left_ = np.concatenate(
        (left_, left[np.argwhere(left[:, 1] == start[1] + 50)]), axis=0
    )
    left_ = np.concatenate(
        (left_, left[np.argwhere(left[:, 1] == start[1] + 70)]), axis=0
    )
    left_ = np.concatenate(
        (left_, left[np.argwhere(left[:, 1] == start[1] + 90)]), axis=0
    ).squeeze(axis=1)
    left_top = np.mean(left_, axis=0, dtype=np.int64)
    right = convexhull_Contours[
        np.argwhere(convexhull_Contours[:, 0] > start[0]).squeeze()
    ]
    right_ = right[np.argwhere(right[:, 1] == start[1] + 10)]
    right_ = np.concatenate(
        (right_, right[np.argwhere(right[:, 1] == start[1] + 30)]), axis=0
    )
    right_ = np.concatenate(
        (right_, right[np.argwhere(right[:, 1] == start[1] + 50)]), axis=0
    )
    right_ = np.concatenate(
        (right_, right[np.argwhere(right[:, 1] == start[1] + 70)]), axis=0
    )
    right_ = np.concatenate(
        (right_, right[np.argwhere(right[:, 1] == start[1] + 90)]), axis=0
    ).squeeze(axis=1)
    right_top = np.mean(right_, axis=0, dtype=np.int64)

    # get bottom left and right points
    convexhull_Contours = np.argwhere(convexhull_img == 255)[:, ::-1]
    left = convexhull_Contours[
        np.argwhere(convexhull_Contours[:, 0] < end[0]).squeeze()
    ]
    left_ = left[np.argwhere(left[:, 1] == end[1] - 10)]
    left_ = np.concatenate(
        (left_, left[np.argwhere(left[:, 1] == end[1] - 30)]), axis=0
    )
    left_ = np.concatenate(
        (left_, left[np.argwhere(left[:, 1] == end[1] - 50)]), axis=0
    )
    left_ = np.concatenate(
        (left_, left[np.argwhere(left[:, 1] == end[1] - 70)]), axis=0
    )
    left_ = np.concatenate(
        (left_, left[np.argwhere(left[:, 1] == end[1] - 90)]), axis=0
    ).squeeze(axis=1)
    left_bottom = np.mean(left_, axis=0, dtype=np.int64)
    right = convexhull_Contours[
        np.argwhere(convexhull_Contours[:, 0] > end[0]).squeeze()
    ]
    right_ = right[np.argwhere(right[:, 1] == end[1] - 10)]
    right_ = np.concatenate(
        (right_, right[np.argwhere(right[:, 1] == end[1] - 30)]), axis=0
    )
    right_ = np.concatenate(
        (right_, right[np.argwhere(right[:, 1] == end[1] - 50)]), axis=0
    )
    right_ = np.concatenate(
        (right_, right[np.argwhere(right[:, 1] == end[1] - 70)]), axis=0
    )
    right_ = np.concatenate(
        (right_, right[np.argwhere(right[:, 1] == end[1] - 90)]), axis=0
    ).squeeze(axis=1)
    right_bottom = np.mean(right_, axis=0, dtype=np.int64)

    # get entire angles
    angle_left_most = get_angle_point(left_most, start)
    angle_right_most = get_angle_point(right_most, start)
    angle_whole = angle_left_most + angle_right_most

    # get top angles
    if left_top[0] > start[0] or left_top[1] < start[1]:
        angle_left_top = 0
    else:
        angle_left_top = get_angle_point(left_top, start)
    if right_top[0] < start[0] or right_top[1] < start[1]:
        angle_right_top = 0
    else:
        angle_right_top = get_angle_point(right_top, start)
    angle_top = angle_left_top + angle_right_top

    # get bottom angles
    if left_bottom[0] > end[0] or left_bottom[1] > end[1]:
        angle_left_bottom = 0
    else:
        if left_bottom[0] < start[0]:
            angle_left_bottom = get_angle_point(left_bottom, start)
        else:
            # a negative value means the left angle is at the right than start point
            angle_left_bottom = -get_angle_point(left_bottom, start)
    if right_bottom[0] < end[0] or right_bottom[1] > end[1]:
        angle_right_bottom = 0
    else:
        if right_bottom[0] > start[0]:
            angle_right_bottom = get_angle_point(right_bottom, start)
        else:
            # a negative value means the right angle is at the left than start point
            angle_right_bottom = -get_angle_point(right_bottom, start)
    angle_bottom = angle_left_bottom + angle_right_bottom
    return (
        angle_whole,
        angle_top,
        angle_bottom,
        angle_left_most,
        angle_right_most,
        angle_left_top,
        angle_right_top,
        angle_left_bottom,
        angle_right_bottom,
    )
