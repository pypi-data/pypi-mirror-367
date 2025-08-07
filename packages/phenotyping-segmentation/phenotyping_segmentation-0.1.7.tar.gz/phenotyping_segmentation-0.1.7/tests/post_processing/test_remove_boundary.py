import glob
import os

import pytest

from phenotyping_segmentation.post_processing.remove_boundary import (
    remove_boundary,
    remove_boundary_from_folder,
)
from tests.fixtures.data import (
    input_dir_clearpot,
    original_images_clearpot_image_1_name,
)


@pytest.fixture
def height():
    return 4512


@pytest.fixture
def width():
    return 10800 + 1024


@pytest.fixture
def seg_name(input_dir_clearpot):
    return (
        input_dir_clearpot
        + "/segmentation_stitch/canola_center/Canola_Batch_F/6525_1_2023-02-21_10-47.png"
    )


@pytest.fixture
def stitch_folder(input_dir_clearpot):
    return input_dir_clearpot + "/segmentation_stitch"


@pytest.fixture
def save_folder(input_dir_clearpot):
    return os.path.join(input_dir_clearpot, "segmentation_noBoundary")


def test_remove_boundary(seg_name, height, width):
    cropped_image = remove_boundary(seg_name, height, width)
    assert cropped_image.shape[0] == height
    assert cropped_image.shape[1] == width


def test_remove_boundary_from_folder(stitch_folder, height, width, save_folder):
    remove_boundary_from_folder(stitch_folder, height, width)

    seg_files = glob.glob(os.path.join(save_folder, "**", "*.png"), recursive=True)
    assert len(seg_files) == 4
