from phenotyping_segmentation.post_processing.buffer import buffer, within_buffer
import pytest


@pytest.fixture
def bbox():
    return [150, 150, 50, 50]


@pytest.fixture
def bbox_0():
    return [0, 0, 100, 100]


@pytest.fixture
def ratio_11():
    return 1.1


def test_buffer(bbox, ratio_11):
    left, top, width, height = buffer(bbox, ratio_11)
    assert left == 148
    assert top == 148
    assert width == 55
    assert height == 55


def test_buffer_0(bbox_0, ratio_11):
    left, top, width, height = buffer(bbox_0, ratio_11)
    assert left == 0
    assert top == 0
    assert width == 110
    assert height == 110


def test_within_buffer(bbox, bbox_0):
    within = within_buffer(bbox, bbox_0)
    assert within == False
