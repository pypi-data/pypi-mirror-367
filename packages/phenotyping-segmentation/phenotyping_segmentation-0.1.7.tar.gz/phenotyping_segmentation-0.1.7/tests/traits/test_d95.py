import cv2
import numpy as np
import pytest

from phenotyping_segmentation.traits.d95 import d95_model
from tests.fixtures.data import seg_1, seg_clearpot_1


@pytest.fixture
def nlayer():
    return 50


@pytest.fixture
def nlayer_17():
    return 17


@pytest.fixture
def im_depth(seg_1):
    seg = cv2.imread(seg_1)
    im_depth = seg.shape[0]
    return im_depth


@pytest.fixture
def im_depth_clearpot(seg_clearpot_1):
    seg = cv2.imread(seg_clearpot_1)
    im_depth_clearpot = seg.shape[0]
    return im_depth_clearpot


@pytest.fixture
def data_pts(seg_1):
    seg = cv2.imread(seg_1, cv2.IMREAD_GRAYSCALE)
    y_indices, x_indices = np.nonzero(seg)
    data_pts = np.column_stack((x_indices, y_indices))
    return data_pts


@pytest.fixture
def data_pts_clearpot(seg_clearpot_1):
    seg = cv2.imread(seg_clearpot_1, cv2.IMREAD_GRAYSCALE)
    y_indices, x_indices = np.nonzero(seg)
    data_pts_clearpot = np.column_stack((x_indices, y_indices))
    return data_pts_clearpot


def test_d95_model(nlayer, im_depth, data_pts):
    beta, r2, d95_layer = d95_model(nlayer, im_depth, data_pts)
    np.testing.assert_almost_equal(beta, 0.95, decimal=2)
    np.testing.assert_almost_equal(r2, 0.90, decimal=2)
    np.testing.assert_equal(d95_layer, 25)


def test_d95_model_clearpot(nlayer_17, im_depth_clearpot, data_pts_clearpot):
    beta, r2, d95_layer = d95_model(nlayer_17, im_depth_clearpot, data_pts_clearpot)
    np.testing.assert_almost_equal(beta, 0.90, decimal=2)
    np.testing.assert_almost_equal(r2, 0.94, decimal=2)
    np.testing.assert_equal(d95_layer, 13)
