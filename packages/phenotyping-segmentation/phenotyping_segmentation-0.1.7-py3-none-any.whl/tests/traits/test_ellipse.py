import cv2
import numpy as np
import pytest

from phenotyping_segmentation.traits.ellipse import fit_ellipse
from tests.fixtures.data import seg_1


@pytest.fixture
def pts(seg_1):
    img = cv2.imread(seg_1, cv2.IMREAD_GRAYSCALE)
    y_indices, x_indices = np.nonzero(img)
    data_pts = np.column_stack((x_indices, y_indices))
    return data_pts


@pytest.fixture
def pts_less5():
    return np.array([[1, 1], [2, 2], [3, 4]])


def test_fit_ellipse(pts):
    a_f, b_f, ratio_ba_f = fit_ellipse(pts)
    np.testing.assert_almost_equal(a_f, 130.34, decimal=2)
    np.testing.assert_almost_equal(b_f, 11.90, decimal=2)
    np.testing.assert_almost_equal(ratio_ba_f, 10.96, decimal=2)


def test_fit_ellipse_less5(pts_less5):
    a_f, b_f, ratio_ba_f = fit_ellipse(pts_less5)
    np.testing.assert_almost_equal(a_f, np.nan, decimal=2)
    np.testing.assert_almost_equal(b_f, np.nan, decimal=2)
    np.testing.assert_almost_equal(ratio_ba_f, np.nan, decimal=2)
