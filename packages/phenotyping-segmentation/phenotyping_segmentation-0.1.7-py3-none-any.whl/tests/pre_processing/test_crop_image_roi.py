import cv2
import numpy as np
import pandas as pd
import pytest

from phenotyping_segmentation.pre_processing.crop_image_roi import (
    crop_save_image,
    crop_save_image_plant,
)
from tests.fixtures.data import original_image_1, scans_csv


@pytest.fixture
def get_image(original_image_1):
    image = cv2.imread(original_image_1)
    return image


@pytest.fixture
def bbox():
    return (540, 56, 1024, 1024)


@pytest.fixture
def crop_path():
    return "tests/data/crop"


@pytest.fixture
def frame():
    return "1.jpg"


@pytest.fixture
def scans_df(scans_csv):
    scans_df = pd.read_csv(scans_csv)
    return scans_df


def test_crop_save_image_roi(get_image, bbox, crop_path, frame):
    new_image, crop_path = crop_save_image(get_image, bbox, crop_path, frame)
    assert new_image.shape == (1024, 1024, 3)


def test_crop_save_image_plant(scans_df):
    save_paths = crop_save_image_plant(scans_df)
    assert len(save_paths) == 8
