import os

import cv2
import numpy as np

from phenotyping_segmentation.post_processing.buffer import buffer, within_buffer
from phenotyping_segmentation.utils.imglist import get_imglist


def remove_unconnection(image_path, save_path, min_size_small, min_size_large):
    """Remove unconnected area for an image.
    Remove any small unconnected area within image center
    Remove any large unconnected area outside the image center

    Args:
    image_path: the original image path.
    min_size_small: the largest unconnected size to remove within a image center.
    min_size_large: the largest unconnected size to remove outside.

    Returns:
        Save the non-unconnected images in the save_path.
    """
    # get image list
    imageList = get_imglist(image_path)

    # check if the save_path exists, if not, create it
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # loop through all images
    for j in range(len(imageList)):
        name = imageList[j]
        im = cv2.imread(os.path.join(image_path, name))
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
        # find all of the connected components (white blobs in your image).
        # im_with_separated_blobs is an image where each detected blob has a different
        # pixel value ranging from 1 to nb_blobs - 1.
        nb_blobs, im_with_separated_blobs, stats, _ = cv2.connectedComponentsWithStats(
            gray
        )

        sizes = stats[:, -1]
        sizes = sizes[1:]
        if len(sizes) > 0:
            nb_blobs -= 1

            # find the largest segment
            bbox = stats[np.argmax(stats[1:, 4]) + 1, 0:4]
            bbox_buffer = buffer(bbox, 1.10)

            im_result = np.zeros_like(im_with_separated_blobs)

            for blob in range(nb_blobs):
                bbox2 = stats[blob + 1, 0:4]
                if within_buffer(bbox_buffer, bbox2):
                    if sizes[blob] >= min_size_small:
                        # see description of im_with_separated_blobs above
                        im_result[im_with_separated_blobs == blob + 1] = 255
                else:
                    if sizes[blob] >= min_size_large:
                        # see description of im_with_separated_blobs above
                        im_result[im_with_separated_blobs == blob + 1] = 255
        else:
            im_result = im
        # save new_image
        save_folder = os.path.join(save_path, "/".join(name.split("/")[:-1]))
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        new_name = os.path.join(save_path, name)
        cv2.imwrite(new_name, im_result)
