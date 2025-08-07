import glob
import os

import pandas as pd
import pytest

from phenotyping_segmentation.pre_processing.crop_pad import (
    add_0padding_crop,
    add_0padding_crop_df,
)
from tests.fixtures.data import (
    input_dir_clearpot,
    input_dir_shoot_maize,
    original_images_clearpot_image_1_name,
)


@pytest.fixture
def crop_path(input_dir_clearpot):
    return input_dir_clearpot + "/crop/canola_center/Canola_Batch_F"


def test_add_0padding_crop(
    input_dir_clearpot, crop_path, original_images_clearpot_image_1_name
):
    patch_size = 1024
    overlap_size = 256

    name_crop_paths = add_0padding_crop(
        patch_size,
        overlap_size,
        original_images_clearpot_image_1_name,
        crop_path,
    )
    assert len(name_crop_paths) == 78
    assert os.path.exists(input_dir_clearpot + "/crop")


def test_add_0padding_crop_df(
    input_dir_clearpot,
):
    patch_size = 1024
    overlap_size = 256
    scans_name = "tests/data/clearpot/scans.csv"
    scans_df = pd.read_csv(scans_name)
    image_replace = "/extended_images/"

    save_paths = add_0padding_crop_df(patch_size, overlap_size, scans_df, image_replace)
    assert len(save_paths) == 1
    assert os.path.exists(input_dir_clearpot + "/crop")
    png_files = glob.glob(
        os.path.join(input_dir_clearpot + "/crop", "**", "*.png"), recursive=True
    )
    assert len(png_files) == 336


def test_add_0padding_crop_df_shoot_maize(
    input_dir_shoot_maize,
):
    patch_size = 1024
    overlap_size = 256
    scans_name = "tests/data/shoot_maize/scans.csv"
    scans_df = pd.read_csv(scans_name)
    image_replace = "/png_images/"

    save_paths = add_0padding_crop_df(patch_size, overlap_size, scans_df, image_replace)
    assert len(save_paths) == 2
    assert os.path.exists(input_dir_shoot_maize + "/crop")
    png_files = glob.glob(
        os.path.join(input_dir_shoot_maize + "/crop", "**", "*.png"), recursive=True
    )
    assert len(png_files) == 350
