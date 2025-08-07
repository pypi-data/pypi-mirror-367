import cv2
import numpy as np

from phenotyping_segmentation.traits.skeleton import (
    get_diameter,
    get_root_info,
    get_skeleton,
    get_skeleton_angle,
    get_skeleton_lengths,
)
from tests.fixtures.data import seg_1, seg_good, seg_seperate_branch


def test_skeleton(seg_1):
    img = cv2.imread(seg_1, cv2.IMREAD_GRAYSCALE)
    skeleton = get_skeleton(img)
    assert skeleton is not None
    assert skeleton.shape == (1024, 1024)
    np.testing.assert_array_equal(np.max(skeleton), 255)
    np.testing.assert_array_equal(np.min(skeleton), 0)


def test_skeleton_angle(seg_1):
    img = cv2.imread(seg_1, cv2.IMREAD_GRAYSCALE)
    skeleton = get_skeleton(img)
    angle_avg, shallow, medium, steep, angles, lengths = get_skeleton_angle(skeleton)
    assert len(angles) == 46
    np.testing.assert_array_almost_equal(angles[0], 9.46, decimal=2)
    np.testing.assert_array_almost_equal(angles[10], 14.74, decimal=2)
    np.testing.assert_array_almost_equal(angle_avg, 6.58, decimal=2)
    np.testing.assert_array_almost_equal(
        [shallow, medium, steep], [0, 0.02, 0.98], decimal=2
    )


def test_skeleton_angle_2branches(seg_seperate_branch):
    img = cv2.imread(seg_seperate_branch, cv2.IMREAD_GRAYSCALE)
    skeleton = get_skeleton(img)
    angle_avg, shallow, medium, steep, angles, lengths = get_skeleton_angle(skeleton)
    assert len(angles) == 70
    assert len(lengths) == 70
    np.testing.assert_array_almost_equal(angles[0], 4.76, decimal=2)
    np.testing.assert_array_almost_equal(angles[10], 0, decimal=2)
    np.testing.assert_array_almost_equal(angle_avg, 7.12, decimal=2)
    np.testing.assert_array_almost_equal(
        [shallow, medium, steep], [0, 0.09, 0.91], decimal=2
    )


def test_skeleton_angle_good(seg_good):
    img = cv2.imread(seg_good, cv2.IMREAD_GRAYSCALE)
    skeleton = get_skeleton(img)
    angle_avg, shallow, medium, steep, angles, lengths = get_skeleton_angle(skeleton)
    assert len(angles) == 74
    assert len(lengths) == 74
    np.testing.assert_array_almost_equal(angles[0], 16.26, decimal=2)
    np.testing.assert_array_almost_equal(angles[10], 56.31, decimal=2)
    np.testing.assert_array_almost_equal(angle_avg, 14.79, decimal=2)
    np.testing.assert_array_almost_equal(
        [shallow, medium, steep], [0, 0.15, 0.85], decimal=2
    )


def test_get_root_info(seg_1):
    img = cv2.imread(seg_1, cv2.IMREAD_GRAYSCALE)
    skeleton_img = get_skeleton(img)
    # skeleton_img = cv2.imread(seg_1, cv2.IMREAD_GRAYSCALE)
    G, root_info = get_root_info(skeleton_img)
    assert isinstance(G, object)
    assert len(root_info) == 12
    assert np.array_equal(root_info["seed_plant"], np.array([177, 538]))
    assert root_info["lateral_num"] == 1
    assert len(root_info["primary_points"]) == 366


def test_get_skeleton_lengths(seg_1):
    img = cv2.imread(seg_1, cv2.IMREAD_GRAYSCALE)
    skeleton = get_skeleton(img)
    (
        total_length,
        primary_root_length,
        lateral_root_length,
        lateral_root_number,
        average_lateral_root_length,
    ) = get_skeleton_lengths(skeleton)
    np.testing.assert_array_almost_equal(total_length, 586.38, decimal=2)
    np.testing.assert_array_almost_equal(primary_root_length, 386.54, decimal=2)
    np.testing.assert_array_almost_equal(lateral_root_length, 199.84, decimal=2)
    np.testing.assert_array_almost_equal(lateral_root_number, 1, decimal=0)
    np.testing.assert_array_almost_equal(average_lateral_root_length, 199.84, decimal=2)


def test_get_skeleton_lengths_2branchs(seg_seperate_branch):
    img = cv2.imread(seg_seperate_branch, cv2.IMREAD_GRAYSCALE)
    skeleton = get_skeleton(img)
    (
        total_length,
        primary_root_length,
        lateral_root_length,
        lateral_root_number,
        average_lateral_root_length,
    ) = get_skeleton_lengths(skeleton)
    np.testing.assert_array_almost_equal(total_length, 815.48, decimal=2)
    np.testing.assert_array_almost_equal(primary_root_length, 392.78, decimal=2)
    np.testing.assert_array_almost_equal(lateral_root_length, 422.69, decimal=2)
    np.testing.assert_array_almost_equal(lateral_root_number, 2, decimal=0)
    np.testing.assert_array_almost_equal(average_lateral_root_length, 211.35, decimal=2)


def test_get_diameter(seg_1):
    img = cv2.imread(seg_1, cv2.IMREAD_GRAYSCALE)
    mean_diameter, median_diameter, max_diameter, diameters = get_diameter(img)
    np.testing.assert_array_almost_equal(mean_diameter, 6.62, decimal=2)
    np.testing.assert_array_almost_equal(median_diameter, 6.0, decimal=2)
    np.testing.assert_array_almost_equal(max_diameter, 12.0, decimal=2)
    assert len(diameters) == 549


def test_get_diameter_2braches(seg_seperate_branch):
    img = cv2.imread(seg_seperate_branch, cv2.IMREAD_GRAYSCALE)
    mean_diameter, median_diameter, max_diameter, diameters = get_diameter(img)
    np.testing.assert_array_almost_equal(mean_diameter, 6.49, decimal=2)
    np.testing.assert_array_almost_equal(median_diameter, 6.0, decimal=2)
    np.testing.assert_array_almost_equal(max_diameter, 12.0, decimal=2)
    assert len(diameters) == 756
