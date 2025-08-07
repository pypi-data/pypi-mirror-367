import glob
import os

import pytest

from phenotyping_segmentation.post_processing.remove_right import (
    remove_right,
    remove_right_from_folder,
)
from tests.fixtures.data import input_dir_clearpot


@pytest.fixture
def seg_name(input_dir_clearpot):
    return (
        input_dir_clearpot
        + "/segmentation_noBoundary/canola_center/Canola_Batch_F/6525_1_2023-02-21_10-47.png"
    )


def test_remove_right(seg_name):
    new_image = remove_right(seg_name)
    assert new_image.shape[0] == 4512
    assert new_image.shape[1] == 10800


def test_remove_right_from_folder(input_dir_clearpot):
    remove_right_from_folder(input_dir_clearpot + "/segmentation_noBoundary")
    seg_files = glob.glob(
        os.path.join(input_dir_clearpot, "segmentation", "**", "*.png"),
        recursive=True,
    )
    assert len(seg_files) == 4
