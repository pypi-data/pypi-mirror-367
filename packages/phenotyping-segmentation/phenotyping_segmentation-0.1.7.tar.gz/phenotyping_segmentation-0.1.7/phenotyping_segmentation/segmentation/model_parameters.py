import os

import numpy as np
import pandas as pd
import segmentation_models_pytorch as smp
import torch


def setup_model_parameters(input_dir, model_name, DEVICE):
    """Setup segmentation model parameters.

    Args:
        input_dir: input dir of this pipeline;
        model_name: trained segmentation model name;
        DEVICE: device that conduct segmentation.

    Returns:
        best_model: loaded pytorch model;
        select_classes: selected segmentation classes;
        select_class_rgb_values: RGB values of the selected classes
        preprocessing_fn: preprocessing function.
    """
    # load best saved model checkpoint from the current run
    print(f"Using device: {DEVICE}")
    model_path = str(os.path.join(input_dir, model_name) + ".pth")
    if os.path.exists(model_path):
        best_model = torch.load(model_path, map_location=DEVICE)
        print(f"Loaded UNet model ({model_path}) from this run.")
    else:
        raise ValueError(f"Model ({model_path}) not available!")
    # setup model parameters
    ENCODER = "resnet101"
    ENCODER_WEIGHTS = "imagenet"
    preprocessing_fn = smp.encoders.get_preprocessing_fn(ENCODER, ENCODER_WEIGHTS)
    # check the color
    class_dict = pd.read_csv(os.path.join(input_dir, "label_class_dict_lr.csv"))
    class_names = class_dict["name"].tolist()
    class_rgb_values = class_dict[["r", "g", "b"]].values.tolist()
    select_classes = class_names
    select_class_indices = [class_names.index(cls.lower()) for cls in select_classes]
    select_class_rgb_values = np.array(class_rgb_values)[select_class_indices]
    return best_model, select_classes, select_class_rgb_values, preprocessing_fn
