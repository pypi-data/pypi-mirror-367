import numpy as np


def get_area_pixel(img):
    """Get area or total number of pixels.

    Args:
        img: root segmentation image as array.

    Returns:
        number of root pixels.
    """
    return np.count_nonzero(img)


def get_area_layer(img, layer_number):
    """Get area of layers with same depth.

    Args:
        img: root segmentation image as array.
        layer_number: number of layers.

    Returns:
        area of each layer and area ratio of each layer.
    """
    # get height of each layer
    height = img.shape[0]
    layer_height = int(height / layer_number)

    # get total root area
    total_root_area = get_area_pixel(img)

    areas_layer = {}

    for i in range(layer_number):
        seg_layer = img[layer_height * i : layer_height * (i + 1)]
        _, count_layer = np.unique(seg_layer, return_counts=True)
        area_name = f"root_area_layer_{i+1}"
        ratio_name = f"root_area_ratio_layer_{i+1}"
        if len(count_layer) > 1:
            areas_layer[area_name] = count_layer[1]
            areas_layer[ratio_name] = count_layer[1] / total_root_area
        else:
            areas_layer[area_name] = 0
            areas_layer[ratio_name] = 0

    return areas_layer
