import math
import os

import cv2
import numpy as np
import pandas as pd

from phenotyping_segmentation.utils.imglist import get_imglist


def stitch_crop(patch_size, overlap_size, original_image_path, seg_path, stitch_path):
    """Stitch the prediction in patch size.

    Args:
        patch_size: expected patch size of deep learning model.
        overlap_size: the expected overlap/border of two adjacent images.
        original_image_path: the path where store original images.
        seg_path: the path where store prediction in patch size.
        stitch_path: the expected path where store the stitched predictions.

    Returns:
        Save stitched predictions.
    """
    seg_dir = os.path.dirname(seg_path)
    seg_basename = os.path.basename(seg_path)

    im = cv2.imread(original_image_path)
    shape_0, shape_1, shape_2 = im.shape[0], im.shape[1], im.shape[2]
    n_0, n_1 = math.ceil(shape_0 / (patch_size - overlap_size / 2)), math.ceil(
        shape_1 / (patch_size - overlap_size / 2)
    )

    n_0_idx = []
    n_1_idx = []
    index = []
    ind = 0
    # index of row and column
    for i in range(n_0):
        for j in range(n_1):
            ind += 1
            n_0_idx.append(i)
            n_1_idx.append(j)
            index.append(ind)

    ind_df = pd.DataFrame({"n_0_idx": n_0_idx, "n_1_idx": n_1_idx, "index": index})
    ind_array = np.array(ind_df)

    im_stitch = np.zeros(
        [
            int(n_0 * (patch_size - overlap_size / 2)),
            int(n_1 * (patch_size - overlap_size / 2)),
            shape_2,
        ]
    )
    for i in range(n_0):
        for j in range(n_1):
            # ind += 1
            top = i * (patch_size - overlap_size)
            left = j * (patch_size - overlap_size)
            ind = np.squeeze(
                ind_array[np.where((ind_array[:, 0] == i) & (ind_array[:, 1] == j)), 2]
            )
            im_pred_patch = cv2.imread(seg_path + "_" + str(ind) + ".png")
            if top == 0 and left == 0:
                im_stitch[
                    top : top + patch_size, left : left + patch_size, :
                ] = im_pred_patch
            elif top == 0 and left > 0:
                left_ind = np.squeeze(
                    ind_array[
                        np.where((ind_array[:, 0] == i) & (ind_array[:, 1] == j - 1)),
                        2,
                    ]
                )

                im_left = cv2.imread(seg_path + "_" + str(left_ind) + ".png")

                # get the overlap area (leaft side of im_pred_patch, right side of im_pred_patch_left)
                im_pred_patch_left = im_pred_patch[0:patch_size, 0:overlap_size, :]
                im_left_right = im_left[0:patch_size, -overlap_size:, :]

                # calculate maximum value of overlapping area
                im_stitch[
                    top : top + patch_size, left : left + overlap_size, :
                ] = np.maximum(im_pred_patch_left, im_left_right)
                im_stitch[
                    top : top + patch_size,
                    left + overlap_size - 1 : left + patch_size - 1,
                    :,
                ] = im_pred_patch[0:patch_size, overlap_size - 1 : patch_size - 1, :]

            elif top > 0 and left == 0:
                top_ind = np.squeeze(
                    ind_array[
                        np.where((ind_array[:, 0] == i - 1) & (ind_array[:, 1] == j)),
                        2,
                    ]
                )

                im_top = cv2.imread(seg_path + "_" + str(top_ind) + ".png")

                # get the overlap area (top side of im_pred_patch, bottom side of im_pred_patch_top)
                im_pred_patch_top = im_pred_patch[0:overlap_size, 0:patch_size, :]
                im_top_bottom = im_top[-overlap_size:, 0:patch_size, :]

                # calculate maximum value of overlapping area
                im_stitch[
                    top : top + overlap_size, left : left + patch_size, :
                ] = np.maximum(im_pred_patch_top, im_top_bottom)
                im_stitch[
                    top + overlap_size - 1 : top + patch_size - 1,
                    left : left + patch_size,
                    :,
                ] = im_pred_patch[overlap_size - 1 : patch_size - 1, 0:patch_size, :]
            else:
                top_ind = np.squeeze(
                    ind_array[
                        np.where((ind_array[:, 0] == i - 1) & (ind_array[:, 1] == j)),
                        2,
                    ]
                )
                left_ind = np.squeeze(
                    ind_array[
                        np.where((ind_array[:, 0] == i) & (ind_array[:, 1] == j - 1)),
                        2,
                    ]
                )

                im_top = cv2.imread(seg_path + "_" + str(top_ind) + ".png")
                # get the overlap area (top side of im_pred_patch, bottom side of im_pred_patch_top)
                im_pred_patch_top = im_pred_patch[0:overlap_size, 0:patch_size, :]
                im_top_bottom = im_top[-overlap_size:, 0:patch_size, :]

                im_stitch[
                    top : top + overlap_size, left : left + patch_size, :
                ] = np.maximum(im_pred_patch_top, im_top_bottom)
                im_stitch[
                    top + overlap_size - 1 : top + patch_size - 1,
                    left : left + patch_size,
                    :,
                ] = im_pred_patch[overlap_size - 1 : patch_size - 1, 0:patch_size, :]

                im_left = cv2.imread(seg_path + "_" + str(left_ind) + ".png")
                # get the overlap area (leaft side of im_pred_patch, right side of im_pred_patch_left)
                im_pred_patch_left = im_pred_patch[0:patch_size, 0:overlap_size, :]
                im_left_right = im_left[0:patch_size, -overlap_size:, :]

                # calculate maximum value of overlapping area
                im_stitch[
                    top : top + patch_size, left : left + overlap_size, :
                ] = np.maximum(im_pred_patch_left, im_left_right)
                im_stitch[
                    top : top + patch_size,
                    left + overlap_size - 1 : left + patch_size - 1,
                    :,
                ] = im_pred_patch[0:patch_size, overlap_size - 1 : patch_size - 1, :]

    name_stitch = stitch_path + ".png"
    cv2.imwrite(name_stitch, im_stitch)


def stitch_crop_folder(
    patch_size, overlap_size, original_image_folder, seg_folder, stitch_folder
):
    """Stitch the prediction in patch size.

    Args:
        patch_size: expected patch size of deep learning model.
        overlap_size: the expected overlap/border of two adjacent images.
        original_image_folder: the folder where store original images.
        seg_folder: the folder where store prediction in patch size.
        stitch_folder: the expected folder where store the stitched predictions.

    Returns:
        Save stitched predictions.
    """
    imgs = get_imglist(original_image_folder)

    stitch_paths = []
    for img_name in imgs:
        original_image_path = os.path.join(original_image_folder, img_name).replace(
            "\\", "/"
        )
        seg_path = os.path.join(seg_folder, img_name.split(".")[0]).replace("\\", "/")
        stitch_path = os.path.join(stitch_folder, img_name.split(".")[0]).replace(
            "\\", "/"
        )
        stitch_path_dir = os.path.dirname(stitch_path)
        if not os.path.exists(stitch_path_dir):
            os.makedirs(stitch_path_dir)

        stitch_crop(
            patch_size, overlap_size, original_image_path, seg_path, stitch_path
        )
        stitch_paths.append(stitch_path)
    return stitch_paths
