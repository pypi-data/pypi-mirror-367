import cv2

from phenotyping_segmentation.segmentation.augmentation import (
    get_validation_augmentation,
)
from tests.fixtures.data import crop_image_1


def test_get_validation_augmentation(crop_image_1):
    aug = get_validation_augmentation()
    image = cv2.cvtColor(cv2.imread(crop_image_1), cv2.COLOR_BGR2RGB)
    sample = aug(image=image)
    tensor_image = sample["image"]
    assert tensor_image.shape == (1024, 1024, 3)
