import numpy as np


def get_height(img):
    """Get root system height or depth.

    Args:
        img: root segmentation image as array.

    Returns:
        root system height or depth, y axis locations of root system top and bottom.
    """
    row_sum = np.nansum(img, axis=1)
    if len(row_sum) > 0:
        non_zero_indices = np.nonzero(row_sum)[0]
        if len(non_zero_indices) > 0:
            top = non_zero_indices[0]
            bottom = non_zero_indices[-1]
            height = bottom - top
        else:
            height = 0
            top = bottom = np.nan
    else:
        height = 0
        top = bottom = np.nan
    return height, top, bottom


def get_width(img):
    """Get root system width.

    Args:
        img: root segmentation image as array.

    Returns:
        root system width, x axis locations of root system left and right.
    """
    row_sum = np.sum(img, axis=0)
    non_zero_indices = np.nonzero(row_sum)[0]
    if len(non_zero_indices) > 0:
        left = non_zero_indices[0]
        right = non_zero_indices[-1]
        width = right - left
    else:
        width = 0
        left = right = np.nan
    return width, left, right


def get_height_dist(img):
    """Get root system height distribution.

    Args:
        img: root segmentation image as array.

    Returns:
        statistics of root system height distribution.
    """
    root_y = np.flatnonzero(img == np.max(img)) // img.shape[1]

    if root_y.size == 0:
        return (np.nan,) * 15

    root_y_min = np.min(root_y)
    root_y_max = np.max(root_y)
    root_y_std = np.std(root_y)

    root_y_mean = np.mean(root_y)
    root_y_median = np.median(root_y)
    root_y_p5 = np.percentile(root_y, 5)
    root_y_p25 = np.percentile(root_y, 25)
    root_y_p75 = np.percentile(root_y, 75)
    root_y_p95 = np.percentile(root_y, 95)

    # get the normalized summary based on the height of plant
    height = root_y_max - root_y_min
    root_y_mean_norm = (root_y_mean - root_y_min) / height
    root_y_median_norm = (root_y_median - root_y_min) / height
    root_y_p5_norm = (root_y_p5 - root_y_min) / height
    root_y_p25_norm = (root_y_p25 - root_y_min) / height
    root_y_p75_norm = (root_y_p75 - root_y_min) / height
    root_y_p95_norm = (root_y_p95 - root_y_min) / height

    return (
        root_y_min,
        root_y_max,
        root_y_std,
        root_y_mean,
        root_y_median,
        root_y_p5,
        root_y_p25,
        root_y_p75,
        root_y_p95,
        root_y_mean_norm,
        root_y_median_norm,
        root_y_p5_norm,
        root_y_p25_norm,
        root_y_p75_norm,
        root_y_p95_norm,
    )


def get_centroid(img):
    """Get root system centroid.

    Args:
        img: root segmentation image as array.

    Returns:
        x and y axis locations of root system centroid.
    """
    # Get the coordinates of the non-zero pixels
    y_indices, x_indices = np.nonzero(img)

    # Calculate the centroid
    if len(x_indices) > 0:
        x_centroid = np.mean(x_indices)
        y_centroid = np.mean(y_indices)
    else:
        x_centroid = np.nan
        y_centroid = np.nan

    return x_centroid, y_centroid
