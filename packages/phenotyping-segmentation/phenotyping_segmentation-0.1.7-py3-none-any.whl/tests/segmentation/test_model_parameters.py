import cv2
import numpy as np
import torch.nn as nn

from phenotyping_segmentation.segmentation.model_parameters import (
    setup_model_parameters,
)
from tests.fixtures.data import DEVICE, crop_image_1, input_dir, model_name, params_json


def test_setup_model_parameters(input_dir, model_name, DEVICE, crop_image_1):
    (
        best_model,
        select_classes,
        select_class_rgb_values,
        preprocessing_fn,
    ) = setup_model_parameters(input_dir, model_name, DEVICE)
    preprocessed_image = preprocessing_fn(cv2.imread(crop_image_1))

    assert isinstance(best_model, nn.Module)
    assert np.array_equal(select_classes, ["background", "root"])
    assert np.array_equal(select_class_rgb_values, [[0, 0, 0], [128, 0, 0]])
    assert np.array_equal(preprocessed_image.shape, [1024, 1024, 3])
    assert preprocessed_image.dtype == np.float64
