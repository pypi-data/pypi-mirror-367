from phenotyping_segmentation.post_processing.stitch_crop import (
    stitch_crop,
    stitch_crop_folder,
)
from tests.fixtures.data import (
    input_dir_clearpot,
    original_images_clearpot_image_1_name,
)
import pytest
import os
import glob


@pytest.fixture
def patch_size():
    return 1024


@pytest.fixture
def overlap_size():
    return 256


@pytest.fixture
def seg_path(input_dir_clearpot):
    return (
        input_dir_clearpot
        + "/segmentation_raw/canola_center/Canola_Batch_F/6525_1_2023-02-21_10-47"
    )


@pytest.fixture
def stitch_path(input_dir_clearpot):
    return (
        input_dir_clearpot
        + "/segmentation_stitch/canola_center/Canola_Batch_F/6525_1_2023-02-21_10-47"
    )


@pytest.fixture
def original_image_folder(input_dir_clearpot):
    return input_dir_clearpot + "/extended_images"


@pytest.fixture
def seg_folder(input_dir_clearpot):
    return input_dir_clearpot + "/segmentation_raw"


@pytest.fixture
def stitch_folder(input_dir_clearpot):
    return input_dir_clearpot + "/segmentation_stitch"


def test_stitch_crop(
    patch_size,
    overlap_size,
    original_images_clearpot_image_1_name,
    seg_path,
    stitch_path,
    input_dir_clearpot,
):
    stitch_crop(
        patch_size,
        overlap_size,
        original_images_clearpot_image_1_name,
        seg_path,
        stitch_path,
    )
    assert os.path.exists(
        input_dir_clearpot + "/segmentation_stitch/canola_center/Canola_Batch_F"
    )


def test_stitch_crop_folder(
    patch_size, overlap_size, original_image_folder, seg_folder, stitch_folder
):
    stitch_paths = stitch_crop_folder(
        patch_size, overlap_size, original_image_folder, seg_folder, stitch_folder
    )
    assert len(stitch_paths) == 4
    assert os.path.exists(stitch_folder)
    png_files = glob.glob(os.path.join(stitch_folder, "**", "*.png"), recursive=True)
    assert len(png_files) == 4
