import cv2
import numpy as np
import pytest

from phenotyping_segmentation.traits.scanline import get_scanline_intersects, get_seed
from phenotyping_segmentation.traits.skeleton import get_skeleton
from tests.fixtures.data import seg_1


@pytest.fixture
def img(seg_1):
    return cv2.imread(seg_1, cv2.IMREAD_GRAYSCALE)


@pytest.fixture
def img_0():
    return np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])


@pytest.fixture
def y_loc():
    return int(1024 / 5)


def test_get_seed(seg_1):
    img = cv2.imread(seg_1, cv2.IMREAD_GRAYSCALE)
    y_indices, x_indices = np.nonzero(img)
    data_pts = np.column_stack((x_indices, y_indices))
    x, y = get_seed(data_pts)
    assert x == 538
    assert y == 175


def test_get_seed_0(img_0):
    y_indices, x_indices = np.nonzero(img_0)
    data_pts = np.column_stack((x_indices, y_indices))
    x, y = get_seed(data_pts)
    assert np.isnan(x)
    assert np.isnan(y)


def test_get_scanline_intersects(img, y_loc):
    root_count, width, left, right = get_scanline_intersects(img, y_loc)
    assert root_count == 1
    assert width == 4
    assert left == 542
    assert right == 546


def test_get_scanline_intersects_0(img_0):
    root_count, width, left, right = get_scanline_intersects(img_0, 1)
    assert np.isnan(root_count)
    assert np.isnan(width)
    assert np.isnan(left)
    assert np.isnan(right)
