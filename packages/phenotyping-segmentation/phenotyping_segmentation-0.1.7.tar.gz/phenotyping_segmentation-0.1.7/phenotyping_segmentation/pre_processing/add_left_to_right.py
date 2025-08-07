import os

import cv2
import numpy as np

from phenotyping_segmentation.utils.imglist import get_imglist


def add_left_to_right(img_name):
    """Add left 1024 pixel columns to right of each image.

    Args:
        img_name: the image name to be add left to right.

    Returns:
        A new image adding left to right.
    """
    image = cv2.imread(img_name)
    new_image = np.zeros((image.shape[0], image.shape[1] + 1024, 3))
    new_image[:, :-1024, :] = image
    new_image[:, -1024:, :] = image[:, :1024, :]
    return new_image


def add_left_to_right_folder(img_folder, ext_folder):
    """Add left 1024 pixel columns to right of each image.

    Args:
        img_folder: the fodler name with images.
        ext_folder: the folder name to save the extended images.

    Returns
        Extended images saved in ext_folder.
    """
    imgs = get_imglist(img_folder)

    for img_name in imgs:
        new_img = add_left_to_right(os.path.join(img_folder, img_name))
        base_fodler = os.path.dirname(img_name)
        new_folder = os.path.join(ext_folder, base_fodler).replace("\\", "/")

        if not os.path.exists(new_folder):
            os.makedirs(new_folder)

        cv2.imwrite(os.path.join(new_folder, os.path.basename(img_name)), new_img)
