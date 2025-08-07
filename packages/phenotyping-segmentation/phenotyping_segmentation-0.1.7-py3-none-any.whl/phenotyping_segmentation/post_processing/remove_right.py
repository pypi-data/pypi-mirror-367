import os

import cv2

from phenotyping_segmentation.utils.imglist import get_imglist


def remove_right(img_name):
    """Remove the right 1024 pixels from the image.

    Args:
        img_name: The name of the image file.

    Returns:
        The image with the right 1024 pixels removed.
    """
    image = cv2.imread(img_name)
    new_image = image[:, :-1024, :]
    return new_image


def remove_right_from_folder(seg_folder):
    """Remove the right 1024 pixels from all images in a folder.

    Args:
        seg_folder: The path to the folder containing images.

    Returns:
        The cropped images are saved in the specified folder.
    """
    seg_files = get_imglist(seg_folder)

    for seg_file in seg_files:
        seg_path = os.path.join(seg_folder, seg_file).replace("\\", "/")
        new_image = remove_right(seg_path)
        save_name = seg_path.replace("/segmentation_noBoundary/", "/segmentation/")
        save_dir = os.path.dirname(save_name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        cv2.imwrite(save_name, new_image)
