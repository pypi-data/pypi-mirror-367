import os

import cv2
from phenotyping_segmentation.utils.imglist import get_imglist


def remove_boundary(seg_name, height, width):
    """Remove the boundary of the segmentation image.

    Args:
        seg_name: The name of the segmentation file.
        height: The expected height of the original image.
        width: The expected width of the original image.

    Returns:
        The image with the boundary removed.
    """
    # get original image and segmentation image shape
    seg = cv2.imread(seg_name)
    height_seg, width_seg = seg.shape[0], seg.shape[1]

    crop_region = (
        int((width_seg - width) / 2),
        int((height_seg - height) / 2),
        width,
        height,
    )

    cropped_image = seg[
        crop_region[1] : crop_region[1] + crop_region[3],
        crop_region[0] : crop_region[0] + crop_region[2],
    ]

    return cropped_image


def remove_boundary_from_folder(stitch_folder, height, width):
    """Remove the boundary of the segmentation images in a folder.

    Args:
        stitch_folder: The path to the folder containing stitched segmentation images.
        height: The expected height of the original images.
        width: The expected width of the original images.

    Returns:
        The cropped images are saved in the specified folder.
    """
    seg_files = get_imglist(stitch_folder)

    for seg_file in seg_files:
        seg_path = os.path.join(stitch_folder, seg_file).replace("\\", "/")
        cropped_image = remove_boundary(seg_path, height, width)
        save_name = seg_path.replace(
            "/segmentation_stitch/", "/segmentation_noBoundary/"
        )
        save_dir = os.path.dirname(save_name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        cv2.imwrite(save_name, cropped_image)
