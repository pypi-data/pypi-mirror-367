import numpy as np


def get_sdx_sdy(data_pts):
    """Get standard deviation of the root points.

    Args:
        data_pts: Root pixel locations as an array of shape (n, 2).

    Return:
        sdx: standard deviation of root location in x axis;
        sdy: standard deviation of toot location in y axis.
    """
    # get x and y locations of root points
    pts_x = data_pts[:, 0]
    pts_y = data_pts[:, 1]

    # get standard deviations
    sdx = np.nanstd(pts_x)
    sdy = np.nanstd(pts_y)
    sdxy = np.divide(sdx, sdy)
    return sdx, sdy, sdxy
