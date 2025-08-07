import cv2
import numpy as np
import pytest

from phenotyping_segmentation.traits.area import get_area_layer, get_area_pixel
from tests.fixtures.data import seg_1, seg_clearpot_1


@pytest.fixture
def img_0():
    return np.array([0, 0, 0, 0])


@pytest.fixture
def layer_number():
    return 17


def test_get_area_pixel(seg_1):
    img = cv2.imread(seg_1)
    area = get_area_pixel(img)
    assert area == 10632


def test_get_area_pixel_0(img_0):
    area = get_area_pixel(img_0)
    assert area == 0


def test_get_area_clearpot_1(seg_clearpot_1):
    img = cv2.imread(seg_clearpot_1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    area = get_area_pixel(img)
    assert area == 1002017


def test_get_area_layer_clearpot_1(seg_clearpot_1, layer_number):
    img = cv2.imread(seg_clearpot_1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    areas_layer = get_area_layer(img, layer_number)
    assert len(areas_layer) == 34
    np.testing.assert_almost_equal(areas_layer["root_area_layer_2"], 124, decimal=0)
    np.testing.assert_almost_equal(
        areas_layer["root_area_ratio_layer_5"], 0.081, decimal=3
    )
