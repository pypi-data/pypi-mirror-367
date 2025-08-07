import pytest
import cv2
import json
import torch
import numpy as np


@pytest.fixture
def original_images():
    """Path to a folder with the original images."""
    return "tests/data/Day8_2024-11-15"


@pytest.fixture
def original_images_clearpot_folder():
    """Path to a folder with the original images."""
    return "tests/data/clearpot/images"


@pytest.fixture
def original_images_clearpot_image_1_name():
    """Path to a folder with the original images."""
    return "tests/data/clearpot/images/canola_center/Canola_Batch_F/6525_1_2023-02-21_10-47.PNG"


@pytest.fixture
def clearpot_ext_folder():
    """Path to a folder with the original images."""
    return "tests/data/clearpot/extended_images"


@pytest.fixture
def clearpot_seg_raw_folder():
    """Path to a folder with the original images."""
    return "tests/data/clearpot/segmentation_raw"


@pytest.fixture
def clearpot_seg_stitch_folder():
    """Path to a folder with the original images."""
    return "tests/data/clearpot/segmentation_stitch"


@pytest.fixture
def input_dir_clearpot():
    """Input directory."""
    return "tests/data/clearpot"


@pytest.fixture
def original_images_shoot_maize_image_1_name():
    """Path to a folder with the original images."""
    return "tests/data/shoot_maize/images/maize/Wave1/0EGG5PJFTH.JPG"


@pytest.fixture
def input_dir_shoot_maize():
    """Input directory."""
    return "tests/data/shoot_maize"


@pytest.fixture
def shoot_maize_seg_folder():
    """Path to a folder with the original images."""
    return "tests/data/shoot_maize/segmentation"


@pytest.fixture
def original_image_1():
    """Path to a folder with the original images."""
    return "tests/data/images/Day8_2024-11-15/C-1/1.jpg"


@pytest.fixture
def crop_image_1():
    """Path to a folder with the original images."""
    return "tests/data/crop/1.jpg"


@pytest.fixture
def crop_label_1():
    """Path to a folder with a label."""
    return "tests/data/label/18_D_R8_19.png"


@pytest.fixture
def seg_1():
    """Path to a folder with a label."""
    return "tests/data/segmentation/Day8_2024-11-15/C-1/1.png"


@pytest.fixture
def seg_clearpot_1():
    """Path to a folder with a label."""
    return "tests/data/clearpot/segmentation/canola_center/Canola_Batch_F/6525_1_2023-02-21_10-47.png"


@pytest.fixture
def seg_seperate_branch():
    """Path to a folder with a label."""
    return "tests/data/segmentation/Day8_2024-11-15/C-10/23.png"


@pytest.fixture
def seg_good():
    """Path to a folder with a label."""
    return "tests/data/segmentation/Day8_2024-11-15/E-3/38.png"


@pytest.fixture
def input_dir():
    """Input directory."""
    return "tests/data"


@pytest.fixture
def output_dir():
    """Output directory."""
    return "tests/data/output"


@pytest.fixture
def params_json():
    """Parameters json file."""
    return "tests/data/params.json"


@pytest.fixture
def model_name(params_json):
    """Trained model name."""
    with open(params_json) as f:
        params = json.load(f)
    model_name = params["model_name"]
    return params["model_name"]


@pytest.fixture
def DEVICE():
    """Get device."""
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return DEVICE


@pytest.fixture
def scans_csv():
    """Path to the scans.csv file."""
    return "tests/data/scans.csv"


@pytest.fixture
def metadata_path():
    """Path to the metadata."""
    return "tests/data/metadata_tem.csv"


@pytest.fixture
def select_class_rgb_values():
    """Selected RGB values for selected classes."""
    return np.array([[0, 0, 0], [128, 0, 0]])
