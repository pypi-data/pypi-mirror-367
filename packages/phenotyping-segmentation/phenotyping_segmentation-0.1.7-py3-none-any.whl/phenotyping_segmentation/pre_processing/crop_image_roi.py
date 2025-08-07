import os

import cv2

from phenotyping_segmentation.utils.imglist import get_imglist


def crop_save_image(image, bbox, crop_path, frame):
    """Crop image and save the cropped images.

    Args:
        image: original image as an array;
        bbox: cropped ROI bounding box with start x and y locations, width, and height;
        crop_path: the path to save cropped images;
        frame: frame name with extension.

    Returns:
        cropped image and the path to save cropped images.
    """
    (roi_x, roi_y, width, height) = bbox
    new_image = image[roi_y : roi_y + height, roi_x : roi_x + width, :]
    cv2.imwrite(os.path.join(crop_path, frame), new_image)
    return new_image, crop_path


def crop_save_image_plant(scans_df):
    """Crop the images for each plant folder.

    Args:
        scans_df: dataframe of scans with a column of plant QR code (plant_qr_code);

    Returns:
        a list of the cropped path of each frame.
    """
    save_paths = []
    for i in range(len(scans_df)):
        scan_path = scans_df["scan_path"][i]
        # create save crop folders, same architecture as scans
        crop_path = scan_path.replace("/images/", "/crop/")
        if not os.path.exists(crop_path):
            os.makedirs(crop_path)
        # get roi with scannerID
        bbox_dic = {
            "1": (350, 56, 1024, 1024),  # FastScanner
            "2": (520, 56, 1024, 1024),  # SlowScanner
            "4": (540, 56, 1024, 1024),  # MainScanner 2025
            # "4": (590, 56, 1024, 1024),  # MainScanner 2024
        }

        # get bounding box with scanner id
        bbox = bbox_dic[str(scans_df["scanner_id"][i])]
        # get the images/frames
        frames = get_imglist(scan_path)
        for frame in frames:
            # crop the original image and save the cropped image
            image_original = cv2.imread(os.path.join(scan_path, frame))
            image, save_path = crop_save_image(image_original, bbox, crop_path, frame)
        save_paths.append(save_path)
    return save_paths
