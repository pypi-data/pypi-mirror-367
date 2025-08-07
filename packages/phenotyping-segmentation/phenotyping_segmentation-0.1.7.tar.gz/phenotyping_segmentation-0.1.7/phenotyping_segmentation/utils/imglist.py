import os


def get_imglist(root_folder):
    """Get the list of images in the segmentation path.

    Args:
        root_folder: the path to the root folder.

    Returns:
        A list of image paths relative to the segmentation path."""

    valid_extensions = (".png", ".jpg", ".jpeg", ".tif", ".bmp")

    imgs = [
        os.path.relpath(os.path.join(root, file), root_folder)
        for root, _, files in os.walk(root_folder)
        for file in files
        if file.lower().endswith(valid_extensions) and not file.startswith(".")
    ]
    imgs = [img.replace("\\", "/") for img in imgs]
    imgs.sort()
    return imgs
