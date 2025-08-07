import os

import cv2
import numpy as np
import pandas as pd

from plantcv import plantcv as pcv

from phenotyping_segmentation.post_processing.buffer import buffer
from phenotyping_segmentation.traits.area import get_area_pixel
from phenotyping_segmentation.traits.convex_hull import conv_hull, get_conv_angles
from phenotyping_segmentation.traits.d95 import d95_model
from phenotyping_segmentation.traits.ellipse import fit_ellipse
from phenotyping_segmentation.traits.height_width import (
    get_centroid,
    get_height,
    get_height_dist,
    get_width,
)
from phenotyping_segmentation.traits.layer_traits import (
    get_layer_imgs,
    get_layer_traits,
)
from phenotyping_segmentation.traits.scanline import get_scanline_intersects
from phenotyping_segmentation.traits.sdxy import get_sdx_sdy
from phenotyping_segmentation.traits.shoot import (
    analyze_stem,
    fill_segments,
    find_branch_stem,
    remove_unconnection_stem,
    segment_sort,
)
from phenotyping_segmentation.traits.skeleton import (
    get_skeleton,
    get_skeleton_angle,
    get_skeleton_lengths,
)
from phenotyping_segmentation.utils.imglist import get_imglist


def get_traits_cylinder(
    seg_path,
    nlayer_d95,
    calculate_layerTraits,
    layerNum_layeredTraits=None,
    plantRegion_layeredTraits=None,
):
    """Get traits of each frame.

    Args:
        seg_path: segmentation filename with path.
        nlayer_d95: number of layers for D95 model.
        calculate_layerTraits: whether to calculate layer traits (True) or not (False).
        layerNum_layeredTraits: number of layers for layered traits.
        plantRegion_layeredTraits: use plant region (True) or whole region (False)
            for layered traits.

    Returns:
        a dataframe with all traits.
    """
    df = pd.DataFrame()
    imgs = get_imglist(seg_path)
    imgs = sorted(imgs, key=lambda x: int("".join(filter(str.isdigit, x))))

    for img_name in imgs:
        frame = os.path.splitext(img_name)[0]
        img_path = os.path.join(seg_path, img_name)
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        if len(img.shape) == 3 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        area = get_area_pixel(img)  # get area
        height, top, bottom = get_height(img)  # get height
        width, left, right = get_width(img)  # get width
        width_depth = np.divide(width, height)  # width to depth ratio
        # get data points (n,2) of x and y locations
        y_indices, x_indices = np.nonzero(img)
        data_pts = np.column_stack((x_indices, y_indices))

        if len(data_pts) > 0:
            sdx, sdy, sdxy = get_sdx_sdy(data_pts)
            a, b, ratio_ba = fit_ellipse(data_pts)  # get ellipse fitting
        else:
            sdx = sdy = sdxy = a = b = ratio_ba = np.nan

        if len(data_pts) > 2:
            hull, chull_area, chull_perimeter = conv_hull(
                data_pts
            )  # get the convex hull
        else:
            chull_perimeter = chull_area = np.nan

        solidity = np.divide(area, chull_area)  # get solidity
        if area > 0:
            # get centroid x and y locations
            x_centroid, y_centroid = get_centroid(img)
            # get skeleton traits
            skeleton = get_skeleton(img)
            # get angle/orientation and length traits
            angle_avg, shallow, medium, steep, angles, lengths = get_skeleton_angle(
                skeleton
            )
            (
                total_length,
                primary_root_length,
                lateral_root_length,
                lateral_root_number,
                average_lateral_root_length,
            ) = get_skeleton_lengths(skeleton)
            # get root system angles with skeleton
            (
                angle_whole,
                angle_top,
                angle_bottom,
                angle_left_most,
                angle_right_most,
                angle_left_top,
                angle_right_top,
                angle_left_bottom,
                angle_right_bottom,
            ) = get_conv_angles(hull, data_pts, skeleton)
            angle_whole_height = np.divide(angle_whole, height)
            angle_top_height = np.divide(angle_top, height)
            angle_bottom_height = np.divide(angle_bottom, height)
            # get layer traits
            if calculate_layerTraits:
                layer_imgs = get_layer_imgs(
                    img, layerNum_layeredTraits, plantRegion_layeredTraits
                )
                layer_traits = get_layer_traits(layer_imgs)
            else:
                layer_traits = {}

        else:
            x_centroid = (
                y_centroid
            ) = (
                angle_avg
            ) = (
                shallow
            ) = (
                medium
            ) = (
                steep
            ) = (
                total_length
            ) = (
                primary_root_length
            ) = (
                lateral_root_length
            ) = lateral_root_number = average_lateral_root_length = np.nan
            angle_whole = (
                angle_top
            ) = (
                angle_bottom
            ) = (
                angle_left_most
            ) = (
                angle_right_most
            ) = (
                angle_left_top
            ) = angle_right_top = angle_left_bottom = angle_right_bottom = np.nan
            angle_whole_height = angle_top_height = angle_bottom_height = np.nan
            layer_traits = {}
        y_loc = np.arange(int(1024 / 5), 1024, int(1024 / 5))
        root_count_0, width_0, left, right = get_scanline_intersects(
            img, y_loc[0]
        )  # get root count and angle at first scanline
        root_count_1, width_1, left, right = get_scanline_intersects(
            img, y_loc[1]
        )  # get root count and angle at second scanline
        root_count_2, width_2, left, right = get_scanline_intersects(
            img, y_loc[2]
        )  # get root count and angle at third scanline
        root_count_3, width_3, left, right = get_scanline_intersects(
            img, y_loc[3]
        )  # get root count and angle at fourth scanline

        # get root pixel distribution in y-axis (verticle axis)
        (
            root_y_min,
            root_y_max,
            root_y_std,
            root_y_mean,
            root_y_median,
            root_y_p5,
            root_y_p25,
            root_y_p75,
            root_y_p95,
            root_y_mean_norm,
            root_y_median_norm,
            root_y_p5_norm,
            root_y_p25_norm,
            root_y_p75_norm,
            root_y_p95_norm,
        ) = get_height_dist(img)

        # D95 model
        im_depth = img.shape[0]
        beta, r2, d95_layer = d95_model(nlayer_d95, im_depth, data_pts)

        data = pd.DataFrame(
            [
                {
                    "plant": seg_path.replace("\\", "/"),
                    "frame": frame,
                    "area": area,
                    "height": height,
                    "width": width,
                    "width_depth": width_depth,
                    "sdx": sdx,
                    "sdy": sdy,
                    "sdxy": sdxy,
                    "a": a,
                    "b": b,
                    "ratio_ba": ratio_ba,
                    "chull_perimeter": chull_perimeter,
                    "chull_area": chull_area,
                    "solidity": solidity,
                    "x_centroid": x_centroid,
                    "y_centroid": y_centroid,
                    "angle_avg": angle_avg,
                    "shallow": shallow,
                    "medium": medium,
                    "steep": steep,
                    "total_length": total_length,
                    "primary_root_length": primary_root_length,
                    "lateral_root_length": lateral_root_length,
                    "lateral_root_number": lateral_root_number,
                    "average_lateral_root_length": average_lateral_root_length,
                    "angle_whole": angle_whole,
                    "angle_top": angle_top,
                    "angle_bottom": angle_bottom,
                    "angle_left_most": angle_left_most,
                    "angle_right_most": angle_right_most,
                    "angle_left_top": angle_left_top,
                    "angle_right_top": angle_right_top,
                    "angle_left_bottom": angle_left_bottom,
                    "angle_right_bottom": angle_right_bottom,
                    "angle_whole_height": angle_whole_height,
                    "angle_top_height": angle_top_height,
                    "angle_bottom_height": angle_bottom_height,
                    "root_count_0": root_count_0,
                    "root_count_1": root_count_1,
                    "root_count_2": root_count_2,
                    "root_count_3": root_count_3,
                    "width_0": width_0,
                    "width_1": width_1,
                    "width_2": width_2,
                    "width_3": width_3,
                    "root_y_min": root_y_min,
                    "root_y_max": root_y_max,
                    "root_y_std": root_y_std,
                    "root_y_mean": root_y_mean,
                    "root_y_median": root_y_median,
                    "root_y_p5": root_y_p5,
                    "root_y_p25": root_y_p25,
                    "root_y_p75": root_y_p75,
                    "root_y_p95": root_y_p95,
                    "root_y_mean_norm": root_y_mean_norm,
                    "root_y_median_norm": root_y_median_norm,
                    "root_y_p5_norm": root_y_p5_norm,
                    "root_y_p25_norm": root_y_p25_norm,
                    "root_y_p75_norm": root_y_p75_norm,
                    "root_y_p95_norm": root_y_p95_norm,
                    "beta": beta,
                    "r2": r2,
                    "d95_layer": d95_layer,
                    **layer_traits,
                }
            ]
        )
        df = pd.concat([df, data])
    return df.reset_index(drop=True)


def get_traits_clearpot(
    seg_path,
    nlayer_d95,
    calculate_layerTraits,
    layerNum_layeredTraits=None,
    plantRegion_layeredTraits=None,
):
    """Get traits of each segmentation mask.

    Args:
        seg_path: segmentation filename with path.
        nlayer_d95: number of layers for D95 model.
        calculate_layerTraits: whether to calculate layer traits (True) or not (False).
        layerNum_layeredTraits: number of layers for layered traits.
        plantRegion_layeredTraits: use plant region (True) or whole region (False)
            for layered traits.

    Returns:
        a dataframe with all traits.
    """
    df = pd.DataFrame()
    imgs = get_imglist(seg_path)
    imgs = sorted(imgs, key=lambda x: int("".join(filter(str.isdigit, x))))

    for img_name in imgs:
        frame = os.path.splitext(img_name)[0]
        img_path = os.path.join(seg_path, img_name)
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        img = img[270:4350, :]  # exclude the top and bottom part of the image
        if len(img.shape) == 3 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        area = get_area_pixel(img)  # get area
        # get data points (n,2) of x and y locations
        y_indices, x_indices = np.nonzero(img)
        data_pts = np.column_stack((x_indices, y_indices))

        if area > 0:
            # get layer traits
            if calculate_layerTraits:
                layer_imgs = get_layer_imgs(
                    img, layerNum_layeredTraits, plantRegion_layeredTraits
                )
                layer_traits = get_layer_traits(layer_imgs)
            else:
                layer_traits = {}

        else:
            layer_traits = {}

        # get root pixel distribution in y-axis (verticle axis)
        (
            root_y_min,
            root_y_max,
            root_y_std,
            root_y_mean,
            root_y_median,
            root_y_p5,
            root_y_p25,
            root_y_p75,
            root_y_p95,
            root_y_mean_norm,
            root_y_median_norm,
            root_y_p5_norm,
            root_y_p25_norm,
            root_y_p75_norm,
            root_y_p95_norm,
        ) = get_height_dist(img)

        # D95 model
        im_depth = img.shape[0]
        beta, r2, d95_layer = d95_model(nlayer_d95, im_depth, data_pts)

        data = pd.DataFrame(
            [
                {
                    "batch": seg_path.replace("\\", "/"),
                    "plant": frame,
                    "area": area,
                    "root_y_min": root_y_min,
                    "root_y_max": root_y_max,
                    "root_y_std": root_y_std,
                    "root_y_mean": root_y_mean,
                    "root_y_median": root_y_median,
                    "root_y_p5": root_y_p5,
                    "root_y_p25": root_y_p25,
                    "root_y_p75": root_y_p75,
                    "root_y_p95": root_y_p95,
                    "root_y_mean_norm": root_y_mean_norm,
                    "root_y_median_norm": root_y_median_norm,
                    "root_y_p5_norm": root_y_p5_norm,
                    "root_y_p25_norm": root_y_p25_norm,
                    "root_y_p75_norm": root_y_p75_norm,
                    "root_y_p95_norm": root_y_p95_norm,
                    "beta": beta,
                    "r2": r2,
                    "d95_layer": d95_layer,
                    **layer_traits,
                }
            ]
        )
        df = pd.concat([df, data])
    return df.reset_index(drop=True)


def get_traits_shoot_maize(seg_shoot_path, seg_stem_path):
    """Get traits of each segmentation mask.

    Args:
        seg_shoot_path: shoot segmentation filename with path.
        seg_stem_path: stem segmentation filename with path.

    Returns:
        a dataframe with all traits.
    """
    df_batch = pd.DataFrame()

    seg_shoot_imgs = get_imglist(seg_shoot_path)
    path = seg_shoot_path.split("segmentation/")[1]

    for seg_shoot_img in seg_shoot_imgs:
        seg_shoot_img_path = os.path.join(seg_shoot_path, seg_shoot_img).replace(
            "\\", "/"
        )
        seg_stem_img_path = os.path.join(seg_stem_path, seg_shoot_img).replace(
            "\\", "/"
        )

        # get shoot and stem segmentation images
        shoot_img = cv2.imread(seg_shoot_img_path, cv2.IMREAD_UNCHANGED)
        stem_img = cv2.imread(seg_stem_img_path, cv2.IMREAD_UNCHANGED)
        if np.max(shoot_img) == 0:
            data = pd.DataFrame(
                [
                    {
                        "image_path": os.path.join(path, seg_shoot_img).replace(
                            "\\", "/"
                        ),
                        "shoot_height": 0,
                        "shoot_width": 0,
                        "stem_height_v1": 0,
                        "leaf_number": 0,
                        "leaf_area": 0,
                        "stem_area_v1": 0,
                        "stem_height_v5": 0,
                        "stem_area_v5": 0,
                        "leaf_area_v5": 0,
                    }
                ]
            )

        else:
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

            cropped_mask = shoot_img[btop : btop + bheight, bleft : bleft + bwidth]

            # get skeleton of the roots
            skeleton = pcv.morphology.skeletonize(mask=cropped_mask)
            skeleton, seg_img, edge_objects = pcv.morphology.prune(
                skel_img=skeleton, size=300, mask=cropped_mask
            )

            # Sort segments into primary (stem) objects and secondary (leaf) objects.
            leaf_obj, stem_obj = segment_sort(
                skel_img=skeleton, objects=edge_objects, mask=cropped_mask
            )

            # get leaf counts
            dist_threshold = 100
            leaf_count = find_branch_stem(stem_obj, leaf_obj, dist_threshold)

            # get leaf and stem area
            leaf_area, stem_area = fill_segments(
                mask=cropped_mask,
                objects=edge_objects,
                stem_objects=stem_obj,
                label=seg_shoot_img,
            )

            # get stem_height
            stem_height = analyze_stem(stem_objects=stem_obj, label=seg_shoot_img)

            # get stem height and stem area from stem model
            if np.max(stem_img[:, 500:-500]) == 0:
                stem_height_v2 = stem_area_v2 = leaf_area_v2 = 0
            else:
                # get the largest cluster
                stem_img = remove_unconnection_stem(stem_img)
                height_axis = np.where(np.max(stem_img[:, 500:-500], axis=1) > 0)
                top, bottom = np.min(height_axis), np.max(height_axis)
                stem_height_v2 = abs(top - bottom)

                unique, count = np.unique(stem_img[:, 500:-500], return_counts=True)
                stem_area_v2 = count[1]
                leaf_area_v2 = stem_area + leaf_area - stem_area_v2

            # append new data to the dataframe
            data = pd.DataFrame(
                [
                    {
                        "image_path": os.path.join(path, seg_shoot_img).replace(
                            "\\", "/"
                        ),
                        "shoot_height": height,
                        "shoot_width": width,
                        "stem_height_v1": stem_height,
                        "leaf_number": leaf_count,
                        "leaf_area": leaf_area,
                        "stem_area_v1": stem_area,
                        "stem_height_v5": stem_height_v2,
                        "stem_area_v5": stem_area_v2,
                        "leaf_area_v5": leaf_area_v2,
                    }
                ]
            )

        df_batch = pd.concat([df_batch, data], ignore_index=True)
    return df_batch
