import cv2
import numpy as np
import plantcv.plantcv as pcv
import pytest

from plantcv.plantcv import params
from skimage.segmentation import watershed

from phenotyping_segmentation.post_processing.buffer import buffer
from phenotyping_segmentation.traits.shoot import (
    analyze_stem,
    colorize_label_img,
    fill_segments,
    find_branch_stem,
    remove_unconnection_stem,
    segment_sort,
)


@pytest.fixture
def seg_shoot_img():
    """Skeletonized image for testing."""
    return "tests/data/shoot_maize/segmentation/maize/Wave1/0EGG5PJFTH.png"


@pytest.fixture
def seg_stem_img():
    """Skeletonized image for testing."""
    return "tests/data/shoot_maize/segmentation_stem/maize/Wave1/0EGG5PJFTH.png"


@pytest.fixture
def cropped_mask(seg_shoot_img):
    """Cropped mask for testing."""
    shoot_img = cv2.imread(seg_shoot_img, cv2.IMREAD_UNCHANGED)

    # crop the image with a buffered bounding box
    height_axis = np.where(np.max(shoot_img, axis=1) > 0)
    top, bottom = np.min(height_axis), np.max(height_axis)
    height = abs(top - bottom)

    width_axis = np.where(np.max(shoot_img, axis=0) > 0)
    right, left = np.max(width_axis), np.min(width_axis)
    width = abs(right - left)

    # crop the plant with buffer
    bbox = (left, top, width, height)
    buffer_ratio = 1.1
    (bleft, btop, bwidth, bheight) = buffer(bbox, buffer_ratio)

    return shoot_img[btop : btop + bheight, bleft : bleft + bwidth]


@pytest.fixture
def skeleton(cropped_mask):
    """Skeletonized image for testing."""
    # get skeleton of the roots
    skeleton = pcv.morphology.skeletonize(mask=cropped_mask)
    skeleton, seg_img, edge_objects = pcv.morphology.prune(
        skel_img=skeleton, size=300, mask=cropped_mask
    )
    return skeleton


@pytest.fixture
def edge_objects(cropped_mask):
    """Skeletonized image for testing."""
    # get edge_objects of the roots
    skeleton = pcv.morphology.skeletonize(mask=cropped_mask)
    skeleton, seg_img, edge_objects = pcv.morphology.prune(
        skel_img=skeleton, size=300, mask=cropped_mask
    )
    return edge_objects


def test_segment_sort(skeleton, edge_objects, cropped_mask):
    """Test the segment_sort function."""
    leaf_obj, stem_obj = segment_sort(
        skeleton, edge_objects, mask=cropped_mask, first_stem=True
    )
    assert len(leaf_obj) == 4
    assert len(leaf_obj[1]) == 2008
    assert len(stem_obj) == 3
    assert len(stem_obj[2]) == 612


def test_find_branch_stem(skeleton, edge_objects, cropped_mask):
    dist_threshold = 100
    leaf_obj, stem_obj = segment_sort(
        skeleton, edge_objects, mask=cropped_mask, first_stem=True
    )
    leaf_count = find_branch_stem(stem_obj, leaf_obj, dist_threshold)
    assert leaf_count == 4


def test_colorize_label_img(cropped_mask, edge_objects, skeleton):
    leaf_obj, stem_obj = segment_sort(
        skeleton, edge_objects, mask=cropped_mask, first_stem=True
    )

    h, w = cropped_mask.shape
    markers = np.zeros((h, w), dtype=np.int32)

    objects_unique = list(edge_objects)  # .copy
    if stem_obj is not None:
        objects_unique.append(np.vstack(stem_obj))

    labels = np.arange(len(objects_unique)) + 1
    for i, l in enumerate(labels):
        cv2.drawContours(markers, objects_unique, i, int(l), 5)

    # Fill as a watershed segmentation from contours as markers
    filled_mask = watershed(
        cropped_mask == 0, markers=markers, mask=cropped_mask != 0, compactness=0
    )

    filled_img = colorize_label_img(filled_mask)
    assert filled_img.shape == cropped_mask.shape + (3,)
    value, count = np.unique(filled_img, return_counts=True)
    assert len(value) == 6
    assert len(count) == 6
    np.testing.assert_array_equal(value, np.array([0, 40, 41, 234, 235, 255]))
    np.testing.assert_array_equal(
        count, np.array([7870480, 14835, 31266, 42661, 72177, 174406])
    )


def test_fill_segments(cropped_mask, edge_objects, skeleton, seg_shoot_img):
    leaf_obj, stem_obj = segment_sort(
        skeleton, edge_objects, mask=cropped_mask, first_stem=True
    )
    leaf_area, stem_area = fill_segments(
        mask=cropped_mask,
        objects=edge_objects,
        stem_objects=stem_obj,
        label=seg_shoot_img,
    )

    assert leaf_area == 143140
    assert stem_area == 31266


def test_analyze_stem(skeleton, edge_objects, cropped_mask, seg_shoot_img):
    leaf_obj, stem_obj = segment_sort(
        skeleton, edge_objects, mask=cropped_mask, first_stem=True
    )
    stem_height = analyze_stem(stem_obj, label=seg_shoot_img)
    assert stem_height == 659


def test_remove_unconnection_stem(seg_stem_img):
    stem_img = cv2.imread(seg_stem_img, cv2.IMREAD_UNCHANGED)
    stem_img = remove_unconnection_stem(stem_img)
    value, count = np.unique(stem_img, return_counts=True)
    assert len(value) == 2
    assert len(count) == 2
    np.testing.assert_array_equal(value, np.array([0, 255]))
    np.testing.assert_array_equal(count, np.array([23986735, 13265]))
