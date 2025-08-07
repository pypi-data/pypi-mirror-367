import json
import os
import warnings

from pathlib import Path

import pandas as pd
import torch

from phenotyping_segmentation.post_processing.buffer import *
from phenotyping_segmentation.post_processing.remove_boundary import *
from phenotyping_segmentation.post_processing.remove_right import *
from phenotyping_segmentation.post_processing.remove_unconnected import *
from phenotyping_segmentation.post_processing.stitch_crop import *
from phenotyping_segmentation.pre_processing.add_left_to_right import *
from phenotyping_segmentation.pre_processing.crop_image_roi import *
from phenotyping_segmentation.pre_processing.crop_pad import *
from phenotyping_segmentation.pre_processing.jpg_to_png import *
from phenotyping_segmentation.segmentation.augmentation import *
from phenotyping_segmentation.segmentation.color import *
from phenotyping_segmentation.segmentation.dataset import *
from phenotyping_segmentation.segmentation.metadata import *
from phenotyping_segmentation.segmentation.model_parameters import *
from phenotyping_segmentation.segmentation.one_hot import *
from phenotyping_segmentation.segmentation.preprocessing import *
from phenotyping_segmentation.traits.area import *
from phenotyping_segmentation.traits.convex_hull import *
from phenotyping_segmentation.traits.d95 import *
from phenotyping_segmentation.traits.ellipse import *
from phenotyping_segmentation.traits.get_traits import *
from phenotyping_segmentation.traits.height_width import *
from phenotyping_segmentation.traits.scanline import *
from phenotyping_segmentation.traits.sdxy import *
from phenotyping_segmentation.traits.summary import *
from phenotyping_segmentation.utils.imglist import *
from phenotyping_segmentation.utils.subfolder import *


def pipeline_cylinder(input_dir):
    # ignore RuntimeWarnings
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)
    warnings.filterwarnings("ignore", category=UserWarning)
    # load scans_csv as dataframe
    scans_csv = Path(input_dir, "scans.csv")
    scans_df = pd.read_csv(scans_csv)

    # load params_json as dict
    params_json = Path(input_dir, "params.json")
    with open(params_json) as f:
        params = json.load(f)
    model_name = params["model_name"]
    nlayer_d95 = int(params["nlayer_d95"])
    calculate_layerTraits = params["calculate_layerTraits"]
    layerNum_layeredTraits = int(params["layerNum_layeredTraits"])
    plantRegion_layeredTraits = params["plantRegion_layeredTraits"]

    # add device
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    output_dir = Path(input_dir, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # crop the original image in scans_df and save cropped images in {output}/crop
    crop_paths = crop_save_image_plant(scans_df)

    # write metadata
    metadata_path = write_metadata(crop_paths, input_dir)

    # load segmentation model and parameters
    (
        best_model,
        select_classes,
        select_class_rgb_values,
        preprocessing_fn,
    ) = setup_model_parameters(input_dir, model_name, DEVICE)
    # setup dataset
    test_dataset, test_dataset_vis = setup_dataset(
        metadata_path, select_class_rgb_values, preprocessing_fn
    )

    # predict cropped images
    seg_raw_plant_root_folders = seg_dataset(
        test_dataset, test_dataset_vis, DEVICE, best_model, select_class_rgb_values
    )

    # remove unconnected area
    seg_raw_subfolders = get_subfolders(seg_raw_plant_root_folders)
    min_size_small = 300
    min_size_large = 3000
    seg_plant_root_folders = seg_raw_plant_root_folders.replace(
        "segmentation_raw", "segmentation"
    )
    for subfolder in seg_raw_subfolders:
        remove_unconnection(
            subfolder,
            subfolder.replace("segmentation_raw", "segmentation"),
            min_size_small,
            min_size_large,
        )

    # get traits
    # get all plant folders
    seg_plant_subfolders = []
    valid_extensions = (".png", ".jpg", ".jpeg", ".tif", ".bmp")
    for dirpath, dirnames, filenames in os.walk(seg_plant_root_folders):
        if (
            any(fname.lower().endswith(valid_extensions) for fname in filenames)
            and not dirnames
        ):
            seg_plant_subfolders.append(dirpath)

    # trait analysis
    summary_df = pd.DataFrame()
    for seg_path in seg_plant_subfolders:
        seg_path = seg_path.replace("\\", "/")
        df = get_traits_cylinder(
            seg_path,
            nlayer_d95,
            calculate_layerTraits,
            layerNum_layeredTraits,
            plantRegion_layeredTraits,
        )
        traits_fname = (
            "plant_original_traits/"
            + seg_path.split("/segmentation/")[1].replace("/", "_")
            + ".csv"
        )
        save_name = Path(output_dir, traits_fname)
        save_path = os.path.dirname(save_name)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        df.to_csv(save_name, index=False)

    group_index = "plant"

    # get plant summary
    summary_df = pd.DataFrame()
    for i, seg_path in enumerate(seg_plant_subfolders):
        seg_path = seg_path.replace("\\", "/")
        traits_fname = (
            "plant_original_traits/"
            + seg_path.split("/segmentation/")[1].replace("/", "_")
            + ".csv"
        )
        save_name = Path(output_dir, traits_fname)
        df = pd.read_csv(save_name)
        traits_df = df
        summary_df = get_statistics_df(traits_df, group_index, summary_df)
        # merge the summary dataframe with scans information
        summary_df["scan_path"] = summary_df["plant"].str.replace(
            "/segmentation/", "/images/"
        )
        merged_df = (
            scans_df.assign(
                key=scans_df["scan_path"].apply(
                    lambda x: next(
                        (y for y in summary_df["scan_path"] if x.endswith(y)), None
                    )
                )
            )
            .merge(summary_df, left_on="key", right_on="scan_path", how="left")
            .drop(columns=["key"])
        )
    merged_df.to_csv(
        Path(output_dir, "plant_summarized_traits.csv"),
        index=False,
    )


def pipeline_clearpot(input_dir_clearpot):
    # ignore RuntimeWarnings
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)
    warnings.filterwarnings("ignore", category=UserWarning)
    # load scans_csv as dataframe
    scans_csv = Path(input_dir_clearpot, "scans.csv")
    scans_df = pd.read_csv(scans_csv)

    # load params_json as dict
    params_json = Path(input_dir_clearpot, "params.json")
    with open(params_json) as f:
        params = json.load(f)
    model_name = params["model_name"]
    nlayer_d95 = int(params["nlayer_d95"])
    calculate_layerTraits = params["calculate_layerTraits"]
    layerNum_layeredTraits = int(params["layerNum_layeredTraits"])
    plantRegion_layeredTraits = params["plantRegion_layeredTraits"]
    patch_size = int(params["patch_size"])
    overlap_size = int(params["overlap_size"])

    # add device
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    output_dir = Path(input_dir_clearpot, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # extend image - add left 1024 pixel columns to right of each image
    original_images_folder = Path(input_dir_clearpot, "images")
    extended_images_folder = Path(input_dir_clearpot, "extended_images")
    if not os.path.exists(extended_images_folder):
        os.makedirs(extended_images_folder)
    add_left_to_right_folder(original_images_folder, extended_images_folder)

    # rewrite scans.csv "/images/" change to "/extended_images/"
    scans_df["scan_path"] = scans_df["scan_path"].str.replace(
        "/images/", "/extended_images/"
    )

    # crop the original image in scans_df and save cropped images in {output}/crop
    image_replace = "/extended_images/"
    crop_paths = add_0padding_crop_df(patch_size, overlap_size, scans_df, image_replace)

    # write metadata
    metadata_path = write_metadata(crop_paths, input_dir_clearpot)

    # load segmentation model and parameters
    (
        best_model,
        select_classes,
        select_class_rgb_values,
        preprocessing_fn,
    ) = setup_model_parameters(input_dir_clearpot, model_name, DEVICE)
    # setup dataset
    test_dataset, test_dataset_vis = setup_dataset(
        metadata_path, select_class_rgb_values, preprocessing_fn
    )

    # predict cropped images
    seg_raw_plant_root_folders = seg_dataset(
        test_dataset, test_dataset_vis, DEVICE, best_model, select_class_rgb_values
    )

    # stitch segmentation results
    stitch_folder = input_dir_clearpot + "/segmentation_stitch"
    stitch_paths = stitch_crop_folder(
        patch_size,
        overlap_size,
        extended_images_folder,
        seg_raw_plant_root_folders,
        stitch_folder,
    )

    # remove boundary
    height = 4512
    width = 10800 + 1024
    remove_boundary_from_folder(stitch_folder, height, width)

    # remove right 1024 pixel columns
    remove_right_from_folder(input_dir_clearpot + "/segmentation_noBoundary")

    # get traits
    # get all batch folders
    seg_plant_root_folder = stitch_folder.replace("segmentation_stitch", "segmentation")
    seg_batch_subfolders = []
    valid_extensions = (".png", ".jpg", ".jpeg", ".tif", ".bmp")
    for dirpath, dirnames, filenames in os.walk(seg_plant_root_folder):
        if (
            any(fname.lower().endswith(valid_extensions) for fname in filenames)
            and not dirnames
        ):
            seg_batch_subfolders.append(dirpath)

    # trait analysis
    all_df = pd.DataFrame()
    for seg_path in seg_batch_subfolders:
        seg_path = seg_path.replace("\\", "/")
        df_batch = get_traits_clearpot(
            seg_path,
            nlayer_d95,
            calculate_layerTraits,
            layerNum_layeredTraits,
            plantRegion_layeredTraits,
        )
        traits_fname = (
            "batch_original_traits/"
            + seg_path.split("/segmentation/")[1].replace("/", "_")
            + ".csv"
        )
        save_name = Path(output_dir, traits_fname)
        save_path = os.path.dirname(save_name)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        df_batch.to_csv(save_name, index=False)
        # get all batch traits
        all_df = pd.concat([all_df, df_batch], ignore_index=True)
    all_df = all_df.reset_index(drop=True)
    all_df.to_csv(Path(output_dir, "all_batch_traits.csv"), index=False)


def pipeline_shoot_maize(input_dir_shoot_maize):
    # ignore RuntimeWarnings
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)
    warnings.filterwarnings("ignore", category=UserWarning)
    # load scans_csv as dataframe
    scans_csv = Path(input_dir_shoot_maize, "scans.csv")
    scans_df = pd.read_csv(scans_csv)

    # load params_json as dict
    params_json = Path(input_dir_shoot_maize, "params.json")
    with open(params_json) as f:
        params = json.load(f)
    model_name = params["model_name"]
    nlayer_d95 = int(params["nlayer_d95"])
    calculate_layerTraits = params["calculate_layerTraits"]
    layerNum_layeredTraits = int(params["layerNum_layeredTraits"])
    plantRegion_layeredTraits = params["plantRegion_layeredTraits"]
    patch_size = int(params["patch_size"])
    overlap_size = int(params["overlap_size"])
    stem_model_name = params["stem_model_name"]

    # add device
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    output_dir = Path(input_dir_shoot_maize, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # convert jpg to png
    original_images_folder = Path(input_dir_shoot_maize, "images")
    png_images_folder = Path(input_dir_shoot_maize, "png_images")
    jpg_to_png_folder(original_images_folder, png_images_folder)

    # crop the original image in scans_df and save cropped images in {output}/crop
    image_replace = "/png_images/"
    crop_paths = add_0padding_crop_df(patch_size, overlap_size, scans_df, image_replace)

    # write metadata
    metadata_path = write_metadata(crop_paths, input_dir_shoot_maize)

    ## shoot model
    # load segmentation model and parameters
    (
        best_model,
        select_classes,
        select_class_rgb_values,
        preprocessing_fn,
    ) = setup_model_parameters(input_dir_shoot_maize, model_name, DEVICE)
    # setup dataset
    test_dataset, test_dataset_vis = setup_dataset(
        metadata_path, select_class_rgb_values, preprocessing_fn
    )

    # predict cropped images
    seg_raw_plant_root_folders = seg_dataset(
        test_dataset, test_dataset_vis, DEVICE, best_model, select_class_rgb_values
    )

    # stitch segmentation results
    stitch_folder = input_dir_shoot_maize + "/segmentation_stitch"
    stitch_paths = stitch_crop_folder(
        patch_size,
        overlap_size,
        png_images_folder,
        seg_raw_plant_root_folders,
        stitch_folder,
    )

    # remove boundary
    height = 4000
    width = 6000
    remove_boundary_from_folder(stitch_folder, height, width)

    # remove unconnected area
    seg_raw_subfolders = get_subfolders(
        input_dir_shoot_maize + "/segmentation_noBoundary"
    )
    min_size_small = 1500  # change it from 500 to 1500
    min_size_large = 3000
    for subfolder in seg_raw_subfolders:
        remove_unconnection(
            subfolder,
            subfolder.replace("segmentation_noBoundary", "segmentation"),
            min_size_small,
            min_size_large,
        )

    ## stem model
    # load segmentation model and parameters
    (
        best_model,
        select_classes,
        select_class_rgb_values,
        preprocessing_fn,
    ) = setup_model_parameters(input_dir_shoot_maize, stem_model_name, DEVICE)
    # setup dataset
    test_dataset, test_dataset_vis = setup_dataset(
        metadata_path, select_class_rgb_values, preprocessing_fn
    )

    # predict cropped images
    seg_raw_plant_root_folders = seg_dataset(
        test_dataset, test_dataset_vis, DEVICE, best_model, select_class_rgb_values
    )

    # stitch segmentation results
    stitch_folder = input_dir_shoot_maize + "/segmentation_stitch"
    stitch_paths = stitch_crop_folder(
        patch_size,
        overlap_size,
        png_images_folder,
        seg_raw_plant_root_folders,
        stitch_folder,
    )

    # remove boundary
    height = 4000
    width = 6000
    remove_boundary_from_folder(stitch_folder, height, width)

    # remove unconnected area
    seg_raw_subfolders = get_subfolders(
        input_dir_shoot_maize + "/segmentation_noBoundary"
    )
    min_size_small = 500  # remove 500 piexels as small area for stem
    min_size_large = 3000

    for subfolder in seg_raw_subfolders:
        remove_unconnection(
            subfolder,
            subfolder.replace("segmentation_noBoundary", "segmentation_stem"),
            min_size_small,
            min_size_large,
        )

    # get traits
    # get all batch folders
    seg_shoot_paths = get_subfolders(input_dir_shoot_maize + "/segmentation")
    seg_stem_paths = get_subfolders(input_dir_shoot_maize + "/segmentation_stem")

    # trait analysis
    all_df = pd.DataFrame()
    for seg_shoot_path, seg_stem_path in zip(seg_shoot_paths, seg_stem_paths):
        df_batch = get_traits_shoot_maize(
            seg_shoot_path,
            seg_stem_path,
        )

        traits_fname = (
            "batch_original_traits/"
            + seg_shoot_path.split("/segmentation/")[1].replace("/", "_")
            + ".csv"
        )
        save_name = Path(output_dir, traits_fname)
        save_path = os.path.dirname(save_name)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        df_batch.to_csv(save_name, index=False)
        # get all batch traits
        all_df = pd.concat([all_df, df_batch], ignore_index=True)
    all_df = all_df.reset_index(drop=True)
    all_df.to_csv(Path(output_dir, "all_batch_traits.csv"), index=False)
