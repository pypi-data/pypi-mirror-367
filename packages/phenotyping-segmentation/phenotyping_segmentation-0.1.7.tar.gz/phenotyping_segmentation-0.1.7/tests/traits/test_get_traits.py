import os

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from phenotyping_segmentation.traits.get_traits import (
    get_traits_clearpot,
    get_traits_cylinder,
    get_traits_shoot_maize,
)
from phenotyping_segmentation.utils.subfolder import get_subfolders
from tests.fixtures.data import input_dir_shoot_maize, output_dir, seg_clearpot_1


@pytest.fixture
def seg_path_1():
    return "tests/data/segmentation/Day8_2024-11-15/C-1"


@pytest.fixture
def seg_path():
    return "tests/data/segmentation"


@pytest.fixture
def seg_clearpot_1_batch():
    return "tests/data/clearpot/segmentation/canola_center/Canola_Batch_F"


@pytest.fixture
def seg_shoot_maize_1_batch():
    return "tests/data/shoot_maize/segmentation/maize/Wave1"


@pytest.fixture
def seg_stem_maize_1_batch():
    return "tests/data/shoot_maize/segmentation_stem/maize/Wave1"


def test_get_traits(seg_path_1):
    traits_df = get_traits_cylinder(seg_path_1, True, 50, 3, True)
    traits_df = traits_df.reset_index(drop=True)
    assert traits_df.shape == (72, 103)
    assert traits_df["area"][0] == 3544
    np.testing.assert_almost_equal(traits_df["chull_area"][0], 9235.5, decimal=2)
    np.testing.assert_almost_equal(traits_df["y_centroid"][9], 371.86, decimal=2)
    np.testing.assert_almost_equal(traits_df["root_y_mean"][11], 373.77, decimal=2)
    np.testing.assert_almost_equal(traits_df["angle_top"][20], 13.5, decimal=2)
    np.testing.assert_almost_equal(traits_df["layer_1_angle_avg"][25], 4.65, decimal=2)
    np.testing.assert_almost_equal(traits_df["layer_3_area"][29], 863, decimal=2)
    np.testing.assert_almost_equal(traits_df["angle_whole_height"][32], 0.02, decimal=2)


def test_get_traits_clearpot_1(seg_clearpot_1_batch):
    traits_df = get_traits_clearpot(seg_clearpot_1_batch, True, 50, 3, True)
    traits_df = traits_df.reset_index(drop=True)
    assert traits_df.shape == (4, 60)
    assert traits_df["area"][0] == 1002017
    np.testing.assert_almost_equal(traits_df["root_y_mean"][1], 2297.34, decimal=2)
    np.testing.assert_almost_equal(traits_df["layer_1_angle_avg"][2], 31.29, decimal=2)
    np.testing.assert_almost_equal(traits_df["layer_3_area"][3], 291333, decimal=2)


def test_get_traits_all(seg_path, output_dir):
    layerNum_layeredTraits = 3
    plantRegion_layeredTraits = True
    nlayer_d95 = 50
    calculate_layerTraits = True

    seg_plant_subfolders = []
    valid_extensions = (".png", ".jpg", ".jpeg", ".tif", ".bmp")
    for dirpath, dirnames, filenames in os.walk(seg_path):
        if (
            any(fname.lower().endswith(valid_extensions) for fname in filenames)
            and not dirnames
        ):
            seg_plant_subfolders.append(dirpath)

    for seg_path in seg_plant_subfolders:
        df = get_traits_cylinder(
            os.path.join(seg_path),
            nlayer_d95,
            calculate_layerTraits,
            layerNum_layeredTraits,
            plantRegion_layeredTraits,
        )
        traits_fname = (
            "plant_original_traits"
            + seg_path.split("segmentation")[1].replace("/", "_")
            + ".csv"
        )
        save_name = os.path.join(output_dir, traits_fname)
        save_path = os.path.dirname(save_name)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        df.to_csv(save_name, index=False)
    assert df.shape == (72, 103)


def test_get_traits_shoot_maize_1(seg_shoot_maize_1_batch, seg_stem_maize_1_batch):
    traits_df = get_traits_shoot_maize(seg_shoot_maize_1_batch, seg_stem_maize_1_batch)
    assert traits_df.shape == (5, 10)
    np.testing.assert_almost_equal(traits_df["shoot_height"][1], 2550, decimal=0)
    np.testing.assert_almost_equal(traits_df["stem_area_v1"][2], 61948, decimal=0)
    np.testing.assert_almost_equal(traits_df["leaf_area_v5"][3], 329553, decimal=0)


def test_get_traits_all_shoot_maize(input_dir_shoot_maize):
    output_dir = Path(input_dir_shoot_maize, "output")
    seg_shoot_paths = get_subfolders(input_dir_shoot_maize + "/segmentation")
    seg_stem_paths = get_subfolders(input_dir_shoot_maize + "/segmentation_stem")

    all_df = pd.DataFrame()
    for seg_shoot_path, seg_stem_path in zip(seg_shoot_paths, seg_stem_paths):
        df_batch = get_traits_shoot_maize(
            seg_shoot_path,
            seg_stem_path,
        )

        traits_fname = (
            "batch_original_traits/"
            + seg_shoot_path.split("/segmentation/")[1].replace("/", "_")
            + ".csv"
        )
        save_name = Path(output_dir, traits_fname)
        save_path = os.path.dirname(save_name)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        df_batch.to_csv(save_name, index=False)
        # get all batch traits
        all_df = pd.concat([all_df, df_batch], ignore_index=True)
    # all_df = all_df.reset_index(drop=True)
    all_df.to_csv(Path(output_dir, "all_batch_traits.csv"), index=False)

    assert all_df.shape == (10, 10)
    np.testing.assert_almost_equal(all_df["shoot_height"][1], 2550, decimal=0)
    np.testing.assert_almost_equal(all_df["stem_area_v1"][5], 38267, decimal=0)
    np.testing.assert_almost_equal(all_df["leaf_area_v5"][8], 345629, decimal=0)
