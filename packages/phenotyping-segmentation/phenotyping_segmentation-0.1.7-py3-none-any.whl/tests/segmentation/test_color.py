import cv2
import numpy as np

from phenotyping_segmentation.segmentation.color import colour_code_segmentation
from phenotyping_segmentation.segmentation.model_parameters import (
    setup_model_parameters,
)
from phenotyping_segmentation.segmentation.one_hot import reverse_one_hot
from tests.fixtures.data import DEVICE, crop_label_1, input_dir, model_name, params_json


def test_colour_code_segmentation_label(crop_label_1, input_dir, model_name, DEVICE):
    image = reverse_one_hot(cv2.imread(crop_label_1))
    # change image value of 2 to 1, because only 2 colors (0 and 1)
    image[image == 2] = 1
    value, count = np.unique(image, return_counts=True)
    assert image.shape == (1024, 1024)
    assert np.array_equal(value, np.array([0, 1]))
    assert np.array_equal(count, np.array([1030870, 17706]))

    (
        best_model,
        select_classes,
        select_class_rgb_values,
        preprocessing_fn,
    ) = setup_model_parameters(input_dir, model_name, DEVICE)
    assert np.array_equal(select_class_rgb_values, [[0, 0, 0], [128, 0, 0]])

    x = colour_code_segmentation(image, select_class_rgb_values)
    reshaped_x = x.reshape(-1, 3)
    value, count = np.unique(reshaped_x, return_counts=True, axis=0)

    assert x.shape == (1024, 1024, 3)
    assert np.array_equal(value, [[0, 0, 0], [128, 0, 0]])
    assert np.array_equal(count, np.array([1030870, 17706]))
