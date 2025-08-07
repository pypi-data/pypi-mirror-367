import os

import cv2
import numpy as np
import plantcv.plantcv as pcv

from plantcv.plantcv import color_palette, dilate, outputs, params
from plantcv.plantcv._debug import _debug
from scipy.stats import zscore
from skimage.segmentation import watershed


def segment_sort(skel_img, objects, mask=None, first_stem=True):
    """Sort segments from a skeletonized image into two categories: leaf objects and other objects.

    Inputs:
    skel_img          = Skeletonized image
    objects           = List of contours
    mask              = (Optional) binary mask for debugging. If provided, debug image will be overlaid on the mask.
    first_stem        = (Optional) if True, then the first (bottom) segment always gets classified as stem

    Returns:
    labeled_img       = Segmented debugging image with lengths labeled
    secondary_objects = List of secondary segments (leaf)
    primary_objects   = List of primary objects (stem)

    :param skel_img: numpy.ndarray
    :param objects: list
    :param mask: numpy.ndarray
    :param first_stem: bool
    :return secondary_objects: list
    :return other_objects: list
    """
    # Store debug
    debug = params.debug
    params.debug = None

    secondary_objects = []
    primary_objects = []

    if mask is None:
        labeled_img = np.zeros(skel_img.shape[:2], np.uint8)
    else:
        labeled_img = mask.copy()

    tips_img = pcv.morphology.find_tips(skel_img)
    tips_img = dilate(tips_img, 3, 1)

    # Loop through segment contours
    for i in range(len(objects)):
        cnt = objects[i]
        segment_plot = np.zeros(skel_img.shape[:2], np.uint8)
        cv2.drawContours(segment_plot, objects, i, 255, 1, lineType=8)
        overlap_img = np.logical_and(segment_plot, tips_img)

        # The first contour is the base, and while it contains a tip, it isn't a leaf
        if i == 0 and first_stem:
            primary_objects.append(cnt)
            # Remove the first "tip" since it corresponds to stem not leaf. This helps
            # leaf number to match the number of "tips"
            outputs.observations["default"]["tips"]["value"] = outputs.observations[
                "default"
            ]["tips"]["value"][1:]
            outputs.observations["default"]["tips"]["label"] = outputs.observations[
                "default"
            ]["tips"]["label"][:-1]

        # Sort segments
        else:
            if np.sum(overlap_img) > 0:
                secondary_objects.append(cnt)
            else:
                primary_objects.append(cnt)

    # use the branch points to seperate leaf and stem
    branch_pts_mask = pcv.morphology.find_branch_pts(
        skel_img=skel_img, mask=mask  # , label=label
    )
    branch_loc_y, branch_loc_x = np.where(branch_pts_mask == 255)

    branch_count = branch_loc_x.shape[0]
    if branch_count == len(secondary_objects) - 1:
        return secondary_objects, primary_objects
    else:
        branch_loc_x_avg = np.mean(branch_loc_x)
        # LW calculate the center point of each contour
        cxs = []
        cys = []
        # refine the overlapped leaves (get the average value of x and y)
        for i in range(len(primary_objects)):
            [[cx, cy]] = np.mean(primary_objects[i], axis=0)
            cxs.append(cx)
            cys.append(cy)

        # just use z-score>2 of cxs to remove outliers of primary
        z_scores = zscore(cxs)
        indexs = np.where(abs(z_scores) > 2)[0]

        primary_objects_remove = primary_objects.copy()
        j = 0
        for ind in range(len(indexs)):
            index = indexs[ind - j]
            primary_objects_remove.pop(index)  # delete
            secondary_objects.append(primary_objects[ind])
            j += 1

        return secondary_objects, primary_objects_remove


def find_branch_stem(stem_obj, leaf_obj, dist_threshold):
    """Get the number of branches close to stem objects.

    Parameters
    ----------
    stem_obj : stem contours.
    leaf_obj : leaf contours.
    dist_threshold : threshold between leaf and stem.

    Returns
    -------
    leaf_count : number of leaves that from stem branch.

    """

    grouped_stem = np.vstack(stem_obj)
    distance = []
    for i in range(len(leaf_obj)):
        distance.append(
            np.min(np.linalg.norm(grouped_stem - np.squeeze(leaf_obj[i]), axis=2))
        )
    leaf_count = np.sum(np.array(distance) < dist_threshold)
    return leaf_count


def colorize_label_img(label_img):
    """Color a labeled image

    Inputs:
        label_img = 2d image with int values at every pixel, where the values represent for the class the
                    pixel belongs to
    Outputs:
        colored_img = RGB image

    :param label_img: numpy.ndarray
    :return: colored_img: numpy.ndarray
    """
    labels = np.unique(label_img)
    h, w = label_img.shape
    rgb_vals = color_palette(num=len(labels), saved=False)
    colored_img = np.zeros((h, w, 3), dtype=np.uint8)
    for i, l in enumerate(labels[1:]):
        colored_img[label_img == l] = rgb_vals[i]

    _debug(
        visual=colored_img,
        filename=os.path.join(
            params.debug_outdir, str(params.device) + "_colorized_label_img.png"
        ),
    )

    return colored_img


def fill_segments(mask, objects, stem_objects=None, label=None):
    """Fills masked segments from contours.

    Inputs:
    mask         = Binary image, single channel, object = 1 and background = 0
    objects      = List of contours
    stem_objects = Array of stem contours
    label        = Optional label parameter, modifies the variable name of
                   observations recorded (default = pcv.params.sample_label).

    Returns:
    filled_mask   = Labeled mask

    :param mask: numpy.ndarray
    :param objects: list
    :param stem_objects: numpy.ndarray
    :param label: str
    :return filled_mask: numpy.ndarray
    """
    # Set lable to params.sample_label if None
    if label is None:
        label = params.sample_label

    h, w = mask.shape
    markers = np.zeros((h, w), dtype=np.int32)

    objects_unique = list(objects)  # .copy
    if stem_objects is not None:
        objects_unique.append(np.vstack(stem_objects))

    labels = np.arange(len(objects_unique)) + 1
    for i, l in enumerate(labels):
        cv2.drawContours(markers, objects_unique, i, int(l), 5)

    # Fill as a watershed segmentation from contours as markers
    filled_mask = watershed(mask == 0, markers=markers, mask=mask != 0, compactness=0)

    # Count area in pixels of each segment
    ids, counts = np.unique(filled_mask, return_counts=True)

    # get leaf and stem area
    leaf_area = np.sum(counts[1:-1].tolist())
    stem_area = counts[-1].tolist()

    debug = params.debug
    params.debug = None
    filled_img = colorize_label_img(filled_mask)
    params.debug = debug
    _debug(
        visual=filled_img,
        filename=os.path.join(
            params.debug_outdir, str(params.device) + "_filled_segments_img.png"
        ),
    )

    return leaf_area, stem_area


def analyze_stem(stem_objects, label=None):
    """Calculate angle of segments (in degrees) by fitting a linear regression line to segments.

    Inputs:
    rgb_img       = RGB image to plot debug image
    stem_objects  = List of stem segments (output from segment_sort function)
    label        = optional label parameter, modifies the variable name of observations recorded

    Returns:
    labeled_img    = Stem analysis debugging image

    :param rgb_img: numpy.ndarray
    :param stem_objects: list
    :param label: str
    :return labeled_img: numpy.ndarray
    """
    # Set lable to params.sample_label if None
    if label is None:
        label = params.sample_label

    grouped_stem = np.vstack(stem_objects)

    # Find vertical height of the stem by measuring bounding box
    stem_x, stem_y, width, height = cv2.boundingRect(grouped_stem)
    return height


def remove_unconnection_stem(gray_stem):
    """Remove unconnected small area for an image.
    Remove any small unconnected area within image center
    Remove any large unconnected area outside the image center

    Args:
    gray_stem: gray image of stem segmentation.

    Returns:
        The new segmentation only with the largest area.
    """
    # find all of the connected components (white blobs in your image).
    # im_with_separated_blobs is an image where each detected blob has a different pixel value ranging from 1 to nb_blobs - 1.
    nb_blobs, im_with_separated_blobs, stats, _ = cv2.connectedComponentsWithStats(
        gray_stem
    )

    sizes = stats[:, -1]
    sizes = sizes[1:]
    size_max = np.max(sizes)
    if len(sizes) > 0:
        nb_blobs -= 1
        im_result = np.zeros_like(im_with_separated_blobs)

        for blob in range(nb_blobs):
            if sizes[blob] >= size_max:
                im_result[im_with_separated_blobs == blob + 1] = 255

    else:
        im_result = gray_stem
    return im_result
