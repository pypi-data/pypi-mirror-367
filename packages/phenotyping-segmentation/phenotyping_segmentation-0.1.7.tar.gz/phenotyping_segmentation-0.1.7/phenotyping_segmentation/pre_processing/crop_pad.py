import math
import os

import cv2

from phenotyping_segmentation.utils.imglist import get_imglist


def add_0padding_crop(
    patch_size,
    overlap_size,
    image_name,
    crop_path,
):
    """Add zero padding to the size of image and crop it for patch.

    Args:
        patch_size: expected patch size of deep learning model.
        overlap_size: the expected overlap/border of two adjacent images.
        image_name: the original image name with path.
        crop_path: the path to save the cropped images.

    Returns
        Add padding of current image and save padding images.
    """
    color = [0, 0, 0]  # add zero padding
    name_crop_paths = []

    im = cv2.imread(image_name)
    shape_0, shape_1 = im.shape[0], im.shape[1]
    n_0, n_1 = math.ceil(shape_0 / (patch_size - overlap_size / 2)), math.ceil(
        shape_1 / (patch_size - overlap_size / 2)
    )
    top, bottom = math.ceil(
        (n_0 * (patch_size - overlap_size / 2) - shape_0) / 2
    ), math.floor((n_0 * (patch_size - overlap_size / 2) - shape_0) / 2)
    left, right = math.ceil(
        (n_1 * (patch_size - overlap_size / 2) - shape_1) / 2
    ), math.floor((n_1 * (patch_size - overlap_size / 2) - shape_1) / 2)
    im_pad = cv2.copyMakeBorder(
        im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color
    )

    idx = 0
    for i in range(n_0):
        for j in range(n_1):
            idx += 1
            crop_name = str(os.path.splitext(image_name)[0]) + "_" + str(idx) + ".png"
            top = i * (patch_size - overlap_size)
            left = j * (patch_size - overlap_size)
            im_crop = im_pad[top : top + patch_size, left : left + patch_size, :]
            name_crop = os.path.join(crop_path, os.path.basename(crop_name)).replace(
                "\\", "/"
            )

            base_fodler = os.path.dirname(name_crop)
            if not os.path.exists(base_fodler):
                os.makedirs(base_fodler)

            cv2.imwrite(name_crop, im_crop)
            name_crop_paths.append(name_crop)
    return name_crop_paths


def add_0padding_crop_df(patch_size, overlap_size, scans_df, image_replace):
    """Add zero padding to the size of image and crop it for patch.

    Args:
        patch_size: expected patch size of deep learning model.
        overlap_size: the expected overlap/border of two adjacent images.
        scans_df: dataframe of scans with a column of plant scan path (scan_path);
        image_replace: the string to replace in scan_path to get the correct path for cropping.

    Returns
        Add padding of current image and save padding images.
    """
    color = [0, 0, 0]  # add zero padding
    save_paths = []

    for i in range(len(scans_df)):
        scan_path = scans_df["scan_path"][i].replace("/images/", image_replace)
        # create save crop folders, same architecture as scans
        crop_path = scan_path.replace(image_replace, "/crop/")
        if not os.path.exists(crop_path):
            os.makedirs(crop_path)
        # get the images
        image_list = get_imglist(scan_path)

        # Loop through each image in the scan path
        for name in image_list:
            image_name = os.path.join(scan_path, name).replace("\\", "/")
            name_crop_paths = add_0padding_crop(
                patch_size,
                overlap_size,
                image_name,
                crop_path,
            )
        save_paths.append(crop_path)
    return save_paths
