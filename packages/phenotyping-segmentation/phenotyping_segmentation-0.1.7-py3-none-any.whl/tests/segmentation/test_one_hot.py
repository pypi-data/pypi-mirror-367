import cv2
import numpy as np

from phenotyping_segmentation.segmentation.one_hot import reverse_one_hot
from tests.fixtures.data import crop_label_1


def test_reverse_one_hot_label(crop_label_1):
    image = reverse_one_hot(cv2.imread(crop_label_1))
    value, count = np.unique(image, return_counts=True)
    assert image.shape == (1024, 1024)
    assert np.array_equal(value, np.array([0, 2]))
    assert np.array_equal(count, np.array([1030870, 17706]))
