import os

import cv2
import numpy as np
import pandas as pd
import torch

from phenotyping_segmentation.segmentation.augmentation import (
    get_validation_augmentation,
)
from phenotyping_segmentation.segmentation.color import colour_code_segmentation
from phenotyping_segmentation.segmentation.one_hot import reverse_one_hot
from phenotyping_segmentation.segmentation.preprocessing import (
    crop_image,
    get_preprocessing,
)


class PredictionDataset(torch.utils.data.Dataset):
    """Read images, apply augmentation and preprocessing transformations."""

    def __init__(
        self,
        df,
        class_rgb_values=None,
        augmentation=None,
        preprocessing=None,
    ):
        self.image_paths = df["image_path"].tolist()
        self.class_rgb_values = class_rgb_values
        self.augmentation = augmentation
        self.preprocessing = preprocessing

    def __getitem__(self, i):
        # read images and masks
        image = cv2.cvtColor(cv2.imread(self.image_paths[i]), cv2.COLOR_BGR2RGB)
        names = self.image_paths[i]
        # apply augmentations
        if self.augmentation:
            sample = self.augmentation(image=image)
            image = sample["image"]
        # apply preprocessing
        if self.preprocessing:
            sample = self.preprocessing(image=image)
            image = sample["image"]
        return image, names

    def __len__(self):
        # return length of
        return len(self.image_paths)


def setup_dataset(metadata_path, select_class_rgb_values, preprocessing_fn):
    """Get dataset for segmentation.

    Args:
        metadata_path: metadata filename with path;
        select_class_rgb_values: RGB values of selected classes;
        preprocessing_fn: preprocessing function.

    Returns:
        test_dataset and test_dataset for visualization.
    """
    metadata_df = pd.read_csv(metadata_path)
    test_dataset = PredictionDataset(
        metadata_df,
        augmentation=get_validation_augmentation(),
        preprocessing=get_preprocessing(preprocessing_fn),
        class_rgb_values=select_class_rgb_values,
    )
    test_dataset_vis = PredictionDataset(
        metadata_df,
        class_rgb_values=select_class_rgb_values,
    )
    return test_dataset, test_dataset_vis


def seg_dataset(
    test_dataset, test_dataset_vis, DEVICE, best_model, select_class_rgb_values
):
    """Get the segmentation dataset.

    Args:
        test_dataset: dataset prepared for segmentation;
        test_dataset_vis: dataset visualization prepared for segmentation;
        DEVICE: device to conduct segmentation;
        best_model: loaded pytorch model;
        select_class_rgb_values: RGB values for selected classes.

    Returns:
        seg_folder: root folder where saved segmentations.
    """
    for idx in range(len(test_dataset)):
        image, names = test_dataset[idx]
        # plant segmentation folder
        plant_folder = names.replace("crop", "segmentation_raw").rsplit("/", 1)[0]
        seg_folder = plant_folder.split("segmentation_raw")[0] + "segmentation_raw"
        if not os.path.exists(plant_folder):
            os.makedirs(plant_folder)

        img_name = names.rsplit("/", 1)[-1]
        image_vis = test_dataset_vis[idx][0].astype("uint8")
        true_dimensions = image_vis.shape
        x_tensor = torch.from_numpy(image).to(DEVICE).unsqueeze(0)
        # Predict test image
        pred_mask = best_model(x_tensor)
        pred_mask = pred_mask.detach().squeeze().cpu().numpy()
        # Convert pred_mask from `CHW` format to `HWC` format
        pred_mask = np.transpose(pred_mask, (1, 2, 0))
        # Get prediction channel corresponding to foreground
        pred_mask = crop_image(
            colour_code_segmentation(
                reverse_one_hot(pred_mask), select_class_rgb_values
            ),
            true_dimensions,
        )["image"]
        pred_mask[np.all(pred_mask == [0, 0, 128], axis=-1)] = [255, 255, 255]
        seg_name = (os.path.join(plant_folder, img_name)).replace(".jpg", ".png")
        cv2.imwrite(seg_name, pred_mask)
    return seg_folder
