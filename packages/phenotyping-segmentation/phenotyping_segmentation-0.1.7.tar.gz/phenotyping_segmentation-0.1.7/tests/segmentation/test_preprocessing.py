import albumentations as album
import cv2
import numpy as np

from phenotyping_segmentation.segmentation.preprocessing import (
    crop_image,
    get_preprocessing,
    to_tensor,
)
from tests.fixtures.data import crop_image_1


def test_get_preprocessing():
    preprocessing = get_preprocessing()
    assert isinstance(preprocessing, album.Compose)


def test_to_tensor(crop_image_1):
    image = cv2.imread(crop_image_1)
    tensor_image = to_tensor(image)
    assert tensor_image.shape == (3, 1024, 1024)
    assert tensor_image.dtype == np.float32


def test_crop_image(crop_image_1):
    image = cv2.imread(crop_image_1)
    crop_size = (1024, 1024)
    cropped_image = crop_image(image, crop_size)
    assert cropped_image["image"].shape == (1024, 1024, 3)
