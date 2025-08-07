import segmentation_models_pytorch as smp

from phenotyping_segmentation.segmentation.dataset import seg_dataset, setup_dataset
from phenotyping_segmentation.segmentation.model_parameters import (
    setup_model_parameters,
)
from tests.fixtures.data import (
    DEVICE,
    input_dir,
    metadata_path,
    model_name,
    params_json,
    select_class_rgb_values,
)


def test_setup_dataset(metadata_path, select_class_rgb_values):
    ENCODER = "resnet101"
    ENCODER_WEIGHTS = "imagenet"
    preprocessing_fn = smp.encoders.get_preprocessing_fn(ENCODER, ENCODER_WEIGHTS)

    test_dataset, test_dataset_vis = setup_dataset(
        metadata_path, select_class_rgb_values, preprocessing_fn
    )
    image, names = test_dataset[0]
    assert len(test_dataset) == 576
    assert image.shape == (3, 1024, 1024)
    assert (
        names
        == "x:/users/linwang/phenotyping-segmentation/tests/data/crop/Day8_2024-11-15/C-1/1.jpg"
    )

    image, names = test_dataset_vis[0]
    assert image.shape == (1024, 1024, 3)
    assert (
        names
        == "x:/users/linwang/phenotyping-segmentation/tests/data/crop/Day8_2024-11-15/C-1/1.jpg"
    )


def test_seg_dataset(
    DEVICE, metadata_path, select_class_rgb_values, input_dir, model_name, params_json
):
    ENCODER = "resnet101"
    ENCODER_WEIGHTS = "imagenet"
    preprocessing_fn = smp.encoders.get_preprocessing_fn(ENCODER, ENCODER_WEIGHTS)

    test_dataset, test_dataset_vis = setup_dataset(
        metadata_path, select_class_rgb_values, preprocessing_fn
    )

    (
        best_model,
        select_classes,
        select_class_rgb_values,
        preprocessing_fn,
    ) = setup_model_parameters(input_dir, model_name, DEVICE)

    seg_folder = seg_dataset(
        test_dataset, test_dataset_vis, DEVICE, best_model, select_class_rgb_values
    )

    assert (
        seg_folder
        == "x:/users/linwang/phenotyping-segmentation/tests/data/segmentation_raw"
    )
