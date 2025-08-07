import pytest

from phenotyping_segmentation.post_processing.remove_unconnected import (
    remove_unconnection,
)
from phenotyping_segmentation.utils.subfolder import get_subfolders


@pytest.fixture
def raw_seg_path():
    return "tests/data/segmentation_raw"


@pytest.fixture
def min_size_small():
    return 300


@pytest.fixture
def min_size_large():
    return 3000


def test_remove_unconnection(raw_seg_path, min_size_small, min_size_large):
    seg_raw_subfolders = get_subfolders(raw_seg_path)

    for subfolder in seg_raw_subfolders:
        remove_unconnection(
            subfolder,
            subfolder.replace("segmentation_raw", "segmentation"),
            min_size_small,
            min_size_large,
        )
    assert len(seg_raw_subfolders) == 8
