import glob
import os

from pathlib import Path

import pytest

from phenotyping_segmentation.pre_processing.jpg_to_png import (
    jpg_to_png,
    jpg_to_png_folder,
)
from tests.fixtures.data import (
    input_dir_shoot_maize,
    original_images_shoot_maize_image_1_name,
)


@pytest.fixture
def image_name():
    """Fixture for the image name."""
    return "0EGG5PJFTH.JPG"


@pytest.fixture
def png_path():
    """Fixture for the output PNG path."""
    return "tests/data/shoot_maize/png_images"


def test_jpg_to_png(image_name, png_path, original_images_shoot_maize_image_1_name):
    """Test the jpg_to_png function."""
    img_path = original_images_shoot_maize_image_1_name

    # Ensure the output directory exists
    if not os.path.exists(png_path):
        os.makedirs(png_path)

    jpg_to_png(image_name, img_path, png_path)

    # Check if the PNG file was created
    png_file = os.path.join(
        png_path, os.path.splitext(os.path.basename(img_path))[0] + ".png"
    )
    assert os.path.exists(png_file), f"PNG file {png_file} was not created."
    # Clean up the created PNG file after the test
    os.remove(png_file)


def test_jpg_to_png_folder(input_dir_shoot_maize):
    """Test the jpg_to_png_folder function."""
    original_images_folder = Path(input_dir_shoot_maize, "images")
    png_images_folder = Path(input_dir_shoot_maize, "png_images")
    jpg_to_png_folder(original_images_folder, png_images_folder)

    # Check if the PNG files were created
    png_files = glob.glob(
        os.path.join(png_images_folder, "**", "*.png"), recursive=True
    )
    assert len(png_files) == 10
