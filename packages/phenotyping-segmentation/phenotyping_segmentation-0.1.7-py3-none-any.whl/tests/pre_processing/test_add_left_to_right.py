import glob
import os

import cv2

from phenotyping_segmentation.pre_processing.add_left_to_right import (
    add_left_to_right,
    add_left_to_right_folder,
)
from tests.fixtures.data import (
    clearpot_ext_folder,
    original_images_clearpot_folder,
    original_images_clearpot_image_1_name,
)


def test_add_left_to_right(original_images_clearpot_image_1_name):
    new_image = add_left_to_right(original_images_clearpot_image_1_name)
    assert new_image.shape == (4512, 11824, 3)


def test_add_left_to_right_folder(original_images_clearpot_folder, clearpot_ext_folder):
    add_left_to_right_folder(original_images_clearpot_folder, clearpot_ext_folder)
    # check whether the extended folder is created
    assert os.path.exists(
        os.path.join(
            clearpot_ext_folder,
            "canola_center",
            "Canola_Batch_F",
        )
    )

    # Check if the extended images are created
    extended_images = glob.glob(
        os.path.join(clearpot_ext_folder, "**", "*.png"), recursive=True
    )
    assert len(extended_images) == 4

    # Check if the shape of the first extended image is correct
    first_extended_image = cv2.imread(extended_images[0])
    assert first_extended_image.shape == (4512, 11824, 3)
