import os

from pathlib import Path

import numpy as np
import pandas as pd

from phenotyping_segmentation.pipeline import (
    pipeline_clearpot,
    pipeline_cylinder,
    pipeline_shoot_maize,
)
from tests.fixtures.data import (
    input_dir,
    input_dir_clearpot,
    input_dir_shoot_maize,
    original_images_clearpot_folder,
    output_dir,
)


def test_pipeline_cylinder(input_dir):
    pipeline_cylinder(input_dir)
    output_dir = Path(input_dir, "output")
    assert os.path.exists(Path(input_dir, "crop"))
    assert os.path.exists(Path(input_dir, "segmentation"))
    assert os.path.exists(Path(output_dir, "plant_original_traits"))
    assert os.path.exists(Path(output_dir, "plant_summarized_traits.csv"))

    # Check if the "crop" folder contains exactly 72 files
    crop_folder = Path(input_dir, "crop", "Day8_2024-11-15", "C-1")
    valid_extensions = (".png", ".jpg", ".jpeg", ".tif", ".bmp")
    frames = [
        file
        for file in os.listdir(crop_folder)
        if (not file.startswith(".")) and file.lower().endswith(valid_extensions)
    ]
    assert len(frames) == 72, f"Expected 72 files in 'crop', found {len(frames)}"

    # check summary traits
    summary_df = pd.read_csv(Path(output_dir, "plant_summarized_traits.csv"))
    assert summary_df.shape == (8, 932)
    np.testing.assert_almost_equal(summary_df["sdxy_mean"][1], 0.14, decimal=2)


def test_pipeline_clearpot(input_dir_clearpot):
    pipeline_clearpot(input_dir_clearpot)
    output_dir = Path(input_dir_clearpot, "output")
    assert os.path.exists(Path(input_dir_clearpot, "crop"))
    assert os.path.exists(Path(input_dir_clearpot, "segmentation"))
    # Check if the "segmentation" folder contains 4 test files
    seg_folder = Path(
        input_dir_clearpot, "segmentation", "canola_center", "Canola_Batch_F"
    )
    valid_extensions = (".png", ".jpg", ".jpeg", ".tif", ".bmp")
    frames = [
        file
        for file in os.listdir(seg_folder)
        if (not file.startswith(".")) and file.lower().endswith(valid_extensions)
    ]
    assert (
        len(frames) == 4
    ), f"Expected 4 test files in 'segmentation' folder, found {len(frames)}"

    # check batch traits
    batch_df = pd.read_csv(
        Path(output_dir, "batch_original_traits", "canola_center_Canola_Batch_F.csv")
    )
    assert batch_df.shape == (4, 60)
    np.testing.assert_almost_equal(batch_df["root_y_mean_norm"][1], 0.57, decimal=2)

    # check all traits
    all_df = pd.read_csv(Path(output_dir, "all_batch_traits.csv"))
    assert all_df.shape == (4, 60)
    np.testing.assert_almost_equal(all_df["root_y_mean"][2], 1996.39, decimal=2)


def test_pipeline_shoot_maize(input_dir_shoot_maize):
    pipeline_shoot_maize(input_dir_shoot_maize)
    output_dir = Path(input_dir_shoot_maize, "output")
    assert os.path.exists(Path(input_dir_shoot_maize, "png_images"))
    assert os.path.exists(Path(input_dir_shoot_maize, "crop"))
    assert os.path.exists(Path(input_dir_shoot_maize, "segmentation"))
    # Check if the "segmentation" folder contains 4 test files
    seg_folder = Path(input_dir_shoot_maize, "segmentation", "maize", "Wave1")
    valid_extensions = (".png", ".jpg", ".jpeg", ".tif", ".bmp")
    frames = [
        file
        for file in os.listdir(seg_folder)
        if (not file.startswith(".")) and file.lower().endswith(valid_extensions)
    ]
    assert (
        len(frames) == 5
    ), f"Expected 5 test files in 'segmentation' folder, found {len(frames)}"

    # check batch traits
    batch_df = pd.read_csv(Path(output_dir, "batch_original_traits", "maize_Wave1.csv"))
    assert batch_df.shape == (5, 10)
    np.testing.assert_almost_equal(batch_df["leaf_area"][1], 281130, decimal=0)

    # check all traits
    all_df = pd.read_csv(Path(output_dir, "all_batch_traits.csv"))
    assert all_df.shape == (10, 10)
    np.testing.assert_almost_equal(all_df["leaf_area_v5"][8], 345629, decimal=0)
