from typing import Tuple

import numpy as np

from skimage.measure import EllipseModel


def fit_ellipse(pts: np.ndarray) -> Tuple[float, float, float]:
    """Find a best fit ellipse for the points per frame.

    Args:
        pts: Root landmarks as array of shape (..., 2).

    Returns:
        A tuple of (a, b, ratio) containing the semi-major axis length,
        semi-minor axis length, and the ratio of the major to minor lengths.

        If the ellipse fitting fails, NaNs are returned.
    """
    # Reshape the input array and filter out rows containing NaNs
    pts = pts.reshape(-1, 2)
    pts = pts[~(np.isnan(pts).all(axis=-1))]

    # Check for a minimum number of points to fit an ellipse
    if len(pts) < 5:
        return np.nan, np.nan, np.nan

    # Initialize the ellipse model
    ell = EllipseModel()

    # Try to estimate the ellipse parameters
    try:
        success = ell.estimate(pts)
    except TypeError as e:
        # If the estimation fails, return NaNs
        return np.nan, np.nan, np.nan

    # Check if the estimation was successful
    if success:
        # Extract the ellipse parameters.
        xc, yc, a_f, b_f, theta = ell.params

        # Check for complex numbers in the parameters.
        if np.iscomplex([xc, yc, a_f, b_f, theta]).any():
            return np.nan, np.nan, np.nan

        # Check for invalid (zero or NaN) major or minor axes.
        if np.isnan(a_f) or np.isnan(b_f) or a_f == 0 or b_f == 0:
            return np.nan, np.nan, np.nan

        # Ensure a_f is the semi-major axis and b_f is the semi-minor axis.
        a_f, b_f = np.maximum(a_f, b_f), np.minimum(a_f, b_f)

        # Calculate the ratio of the major to minor axis.
        ratio_ba_f = a_f / b_f

        return a_f, b_f, ratio_ba_f

    else:
        # Return NaNs if the ellipse fitting was not successful.
        return np.nan, np.nan, np.nan
