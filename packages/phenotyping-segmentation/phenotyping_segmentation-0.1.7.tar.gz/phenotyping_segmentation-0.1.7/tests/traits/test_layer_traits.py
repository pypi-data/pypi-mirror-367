import cv2
import numpy as np
import pytest

from phenotyping_segmentation.traits.layer_traits import (
    get_layer_imgs,
    get_layer_traits,
)
from tests.fixtures.data import seg_1


@pytest.fixture
def img(seg_1):
    return cv2.imread(seg_1, cv2.IMREAD_GRAYSCALE)


@pytest.fixture
def layer_num():
    return 3


@pytest.fixture
def plantimg_true():
    return True


@pytest.fixture
def plantimg_false():
    return False


def test_get_layer_imgs(img, layer_num, plantimg_true):
    layer_imgs = get_layer_imgs(img, layer_num, plantRegion_layeredTraits=plantimg_true)
    assert isinstance(layer_imgs, list)
    assert len(layer_imgs) == 3
    assert layer_imgs[0].shape == (123, 1024)
    assert layer_imgs[1].shape == (123, 1024)
    assert layer_imgs[2].shape == (122, 1024)
    # Check that the layers img has root pixel
    assert np.max(layer_imgs[0]) == 255
    assert np.max(layer_imgs[1]) == 255
    assert np.max(layer_imgs[2]) == 255


def test_get_layer_imgs_false(img, layer_num, plantimg_false):
    layer_imgs = get_layer_imgs(
        img, layer_num, plantRegion_layeredTraits=plantimg_false
    )
    assert isinstance(layer_imgs, list)
    assert len(layer_imgs) == 3
    assert layer_imgs[0].shape == (342, 1024)
    assert layer_imgs[1].shape == (342, 1024)
    assert layer_imgs[2].shape == (340, 1024)
    # Check that the layers img has root pixel
    assert np.max(layer_imgs[0]) == 255
    assert np.max(layer_imgs[1]) == 255
    assert np.max(layer_imgs[2]) == 0


def test_get_layer_traits(img, layer_num, plantimg_true):
    layer_imgs = get_layer_imgs(img, layer_num, plantRegion_layeredTraits=plantimg_true)
    traits = get_layer_traits(layer_imgs)
    assert isinstance(traits, dict)
    assert len(traits) == 39
    np.testing.assert_almost_equal(traits["layer_1_area"], 774, decimal=0)
    np.testing.assert_almost_equal(traits["layer_2_solidity"], 0.63, decimal=2)
    np.testing.assert_almost_equal(traits["layer_1_angle_avg"], 6.77, decimal=2)
    np.testing.assert_almost_equal(traits["layer_2_angle_avg"], 8.81, decimal=2)
    np.testing.assert_almost_equal(traits["layer_3_angle_avg"], 8, decimal=2)
    np.testing.assert_almost_equal(traits["layer_1_medium"], 0, decimal=2)
    np.testing.assert_almost_equal(traits["layer_2_medium"], 0.05, decimal=2)
    np.testing.assert_almost_equal(traits["layer_3_medium"], 0, decimal=2)
    np.testing.assert_almost_equal(traits["layer_1_steep"], 1, decimal=2)
    np.testing.assert_almost_equal(traits["layer_2_steep"], 0.95, decimal=2)
    np.testing.assert_almost_equal(traits["layer_3_steep"], 1, decimal=2)
