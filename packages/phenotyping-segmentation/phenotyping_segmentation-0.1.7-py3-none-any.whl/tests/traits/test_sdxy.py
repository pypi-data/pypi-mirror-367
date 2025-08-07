import cv2
import numpy as np
import pytest

from phenotyping_segmentation.traits.sdxy import get_sdx_sdy
from tests.fixtures.data import seg_1


@pytest.fixture
def pts(seg_1):
    img = cv2.imread(seg_1, cv2.IMREAD_GRAYSCALE)
    y_indices, x_indices = np.nonzero(img)
    data_pts = np.column_stack((x_indices, y_indices))
    return data_pts


def test_get_sdx_sdy(pts):
    sdx, sdy, sdxy = get_sdx_sdy(pts)
    np.testing.assert_almost_equal(sdx, 7.98, decimal=2)
    np.testing.assert_almost_equal(sdy, 95.06, decimal=2)
    np.testing.assert_almost_equal(sdxy, 0.08, decimal=2)
