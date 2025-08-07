import cv2
import numpy as np
import pytest

from phenotyping_segmentation.traits.convex_hull import (
    conv_hull,
    get_angle_point,
    get_conv_angles,
)
from phenotyping_segmentation.traits.skeleton import get_skeleton
from tests.fixtures.data import seg_1, seg_good


@pytest.fixture
def pts_3d():
    return np.array([1, 1, 1])


@pytest.fixture
def pts_nan():
    return np.array([[1, 1], [np.nan, 2], [3, 4]])


@pytest.fixture
def pts_less3():
    return np.array([[1, 1], [3, 4], [1, 1]])


def test_conv_hull(seg_1):
    img = cv2.imread(seg_1, cv2.IMREAD_GRAYSCALE)
    y_indices, x_indices = np.nonzero(img)
    data_pts = np.column_stack((x_indices, y_indices))
    hull, chull_area, chull_perimeter = conv_hull(data_pts)
    assert isinstance(hull, object)
    assert np.equal(np.round(chull_perimeter, 2), 755.17)
    assert np.equal(np.round(chull_area, 2), 9235.50)


def test_conv_hull_3d(pts_3d, caplog):
    with pytest.raises(ValueError, match="Input points should be of shape"):
        conv_hull(pts_3d)


def test_conv_hull_nan(pts_nan):
    hull, chull_area, chull_perimeter = conv_hull(pts_nan)
    assert chull_perimeter == None
    assert chull_area == None


def test_conv_hull_less3(pts_less3):
    hull, chull_area, chull_perimeter = conv_hull(pts_less3)
    assert chull_perimeter == None
    assert chull_area == None


def test_get_angle_point(seg_1):
    img = cv2.imread(seg_1, cv2.IMREAD_GRAYSCALE)
    y_indices, x_indices = np.nonzero(img)
    data_pts = np.column_stack((x_indices, y_indices))
    angle = get_angle_point(data_pts[0], data_pts[1])
    np.testing.assert_almost_equal(angle, 135, decimal=2)


def test_get_angle_point_nan(pts_nan):
    angle = get_angle_point(pts_nan[0], pts_nan[1])
    assert np.isnan(angle)


def test_get_conv_angles(seg_1):
    img = cv2.imread(seg_1, cv2.IMREAD_GRAYSCALE)
    y_indices, x_indices = np.nonzero(img)
    data_pts = np.column_stack((x_indices, y_indices))
    skeleton_img = get_skeleton(img)
    hull, _, _ = conv_hull(data_pts)
    (
        angle_whole,
        angle_top,
        angle_bottom,
        angle_left_most,
        angle_right_most,
        angle_left_top,
        angle_right_top,
        angle_left_bottom,
        angle_right_bottom,
    ) = get_conv_angles(hull, data_pts, skeleton_img)
    np.testing.assert_almost_equal(angle_whole, 6.76, decimal=2)
    np.testing.assert_almost_equal(angle_top, 15.84, decimal=2)
    np.testing.assert_almost_equal(angle_bottom, 4.55, decimal=2)
    np.testing.assert_almost_equal(angle_left_most, 2.69, decimal=2)
    np.testing.assert_almost_equal(angle_right_most, 4.07, decimal=2)
    np.testing.assert_almost_equal(angle_left_top, 3.43, decimal=2)
    np.testing.assert_almost_equal(angle_right_top, 12.41, decimal=2)
    np.testing.assert_almost_equal(angle_left_bottom, 2.71, decimal=2)
    np.testing.assert_almost_equal(angle_right_bottom, 1.84, decimal=2)


def test_get_conv_angles_good(seg_good):
    img = cv2.imread(seg_good, cv2.IMREAD_GRAYSCALE)
    y_indices, x_indices = np.nonzero(img)
    data_pts = np.column_stack((x_indices, y_indices))
    skeleton_img = get_skeleton(img)
    hull, _, _ = conv_hull(data_pts)
    (
        angle_whole,
        angle_top,
        angle_bottom,
        angle_left_most,
        angle_right_most,
        angle_left_top,
        angle_right_top,
        angle_left_bottom,
        angle_right_bottom,
    ) = get_conv_angles(hull, data_pts, skeleton_img)
    np.testing.assert_almost_equal(angle_whole, 52.68, decimal=2)
    np.testing.assert_almost_equal(angle_top, 61.79, decimal=2)
    np.testing.assert_almost_equal(angle_bottom, 2.49, decimal=2)
    np.testing.assert_almost_equal(angle_left_most, 12.77, decimal=2)
    np.testing.assert_almost_equal(angle_right_most, 39.91, decimal=2)
    np.testing.assert_almost_equal(angle_left_top, 19.8, decimal=2)
    np.testing.assert_almost_equal(angle_right_top, 42, decimal=2)
    np.testing.assert_almost_equal(angle_left_bottom, 2.08, decimal=2)
    np.testing.assert_almost_equal(angle_right_bottom, 0.41, decimal=2)
