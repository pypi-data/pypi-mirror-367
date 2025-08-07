import os

import numpy as np
import pandas as pd
import pytest

from phenotyping_segmentation.traits.summary import get_statistics, get_statistics_df
from tests.fixtures.data import output_dir, scans_csv


@pytest.fixture
def seg_path():
    return "tests/data/segmentation"


@pytest.fixture
def scans_df(scans_csv):
    return pd.read_csv(scans_csv)


def test_get_statistics(seg_path, output_dir, scans_df):
    seg_plant_subfolders = []
    valid_extensions = (".png", ".jpg", ".jpeg", ".tif", ".bmp")
    for dirpath, dirnames, filenames in os.walk(seg_path):
        if (
            any(fname.lower().endswith(valid_extensions) for fname in filenames)
            and not dirnames
        ):
            seg_plant_subfolders.append(dirpath)
    summary_df = pd.DataFrame()
    for seg_path in seg_plant_subfolders:
        traits_fname = (
            "plant_original_traits"
            + seg_path.split("segmentation")[1].replace("/", "_")
            + ".csv"
        )
        save_name = os.path.join(output_dir, traits_fname)
        save_path = os.path.dirname(save_name)
        df = pd.read_csv(save_name)
        traits_df = df
        group_index = "plant"
        summary_df = get_statistics_df(traits_df, group_index, summary_df)
        # merge the summary dataframe with scans information
        summary_df["scan_path"] = summary_df["plant"].str.replace(
            "segmentation", "images"
        )
        summary_df = summary_df.reset_index(drop=True)
        merged_df = (
            scans_df.assign(
                key=scans_df["scan_path"].apply(
                    lambda x: next((y for y in summary_df["scan_path"] if y in x), None)
                )
            )
            .merge(summary_df, left_on="key", right_on="scan_path", how="left")
            .drop(columns=["key"])
        )

        # merged_df = pd.merge(scans_df, summary_df, on="scan_path")
        merged_df.to_csv(
            os.path.join(output_dir, "plant_summarized_traits.csv"),
            index=False,
        )
    assert summary_df.shape == (8, 911)
    assert merged_df.shape == (8, 932)
    np.testing.assert_almost_equal(summary_df["area_max"][0], 3807)
