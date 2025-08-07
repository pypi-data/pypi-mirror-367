import numpy as np

from phenotyping_segmentation.traits.area import get_area_pixel
from phenotyping_segmentation.traits.convex_hull import conv_hull
from phenotyping_segmentation.traits.height_width import get_height, get_width
from phenotyping_segmentation.traits.sdxy import get_sdx_sdy
from phenotyping_segmentation.traits.skeleton import get_skeleton, get_skeleton_angle


def get_layer_imgs(img, layerNum_LayeredTraits, plantRegion_layeredTraits=True):
    """
    Get the layer images based on the specified layer number.

    Parameters:
    img (numpy.ndarray): The input image (segmentation mask).
    layerNum_LayeredTraits (int): The layer number to extract.
    plantRegion_layeredTraits (bool): Whether the image is just plant area. (PlantRegionOnly)
        Default is True (only use subimage with height of a plant).
        False is use the original segmentation mask.
        plantimg, options, plant region, whole mask, a specific region

    Returns:
    numpy.ndarray: The extracted layer images.
    """
    if plantRegion_layeredTraits is True:
        height, top, bottom = get_height(img)
    else:
        height = img.shape[0]
        top = 0
        bottom = height
    layer_thickness = np.ceil(height / layerNum_LayeredTraits)
    layer_imgs = []
    for i in range(layerNum_LayeredTraits):
        start = int(top + i * layer_thickness)
        end = int(
            min(top + (i + 1) * layer_thickness, bottom)
        )  # make sure not to exceed bottom
        layer = img[start:end, :]  # vertical slicing (axis 0), all columns
        layer_imgs.append(layer)
    return layer_imgs


def get_layer_traits(layer_imgs):
    """Get the traits of each layer.

    Args:
        layer_imgs (list): List of layer images.

    Returns:
        list: list of traits for each layer.
    """
    traits = []
    for i, img in enumerate(layer_imgs):
        area = get_area_pixel(img)
        height, top, bottom = get_height(img)
        width, left, right = get_width(img)

        y_indices, x_indices = np.nonzero(img)
        data_pts = np.column_stack((x_indices, y_indices))

        if len(data_pts) > 0:
            sdx, sdy, sdxy = get_sdx_sdy(data_pts)
        else:
            sdx = sdy = sdxy = np.nan

        if len(data_pts) > 2:
            hull, chull_area, chull_perimeter = conv_hull(
                data_pts
            )  # get the convex hull
        else:
            chull_perimeter = chull_area = np.nan

        solidity = np.divide(area, chull_area)  # get solidity

        skeleton = get_skeleton(img)
        angle_avg, shallow, medium, steep, angles, lengths = get_skeleton_angle(
            skeleton
        )
        traits.append(
            {
                f"layer_{i+1}_area": area,
                f"layer_{i+1}_height": height,
                f"layer_{i+1}_width": width,
                f"layer_{i+1}_sdx": sdx,
                f"layer_{i+1}_sdy": sdy,
                f"layer_{i+1}_sdxy": sdxy,
                f"layer_{i+1}_chull_perimeter": chull_perimeter,
                f"layer_{i+1}_chull_area": chull_area,
                f"layer_{i+1}_solidity": solidity,
                f"layer_{i+1}_angle_avg": angle_avg,
                f"layer_{i+1}_shallow": shallow,
                f"layer_{i+1}_medium": medium,
                f"layer_{i+1}_steep": steep,
            }
        )
        flat_traits = {k: v for d in traits for k, v in d.items()}
    return flat_traits
