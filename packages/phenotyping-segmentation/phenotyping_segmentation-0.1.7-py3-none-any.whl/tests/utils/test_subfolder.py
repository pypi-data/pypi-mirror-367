from phenotyping_segmentation.utils.subfolder import get_subfolders
import pytest


@pytest.fixture
def raw_seg_path():
    return "tests/data/segmentation_raw"


def test_get_subfolders(raw_seg_path):
    subfolders = get_subfolders(raw_seg_path)
    assert len(subfolders) == 7
    assert subfolders[0] == "tests/data/segmentation_raw\Day8_2024-11-15\C-1"
