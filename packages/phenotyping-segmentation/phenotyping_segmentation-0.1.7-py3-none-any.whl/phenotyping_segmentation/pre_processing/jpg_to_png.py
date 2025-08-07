import os

from PIL import Image


def jpg_to_png(image_name, img_path, png_path):
    """Convert jpg file to png file.

    Args:
        image_name (str): Name of the image file.
        img_path (str): Path to the image file.
        png_path (str): Path where the converted png file will be saved.

    Returns:
        Saved png files.
    """
    if os.path.splitext(image_name)[1] == ".JPG":
        im = Image.open(img_path)
        filename = os.path.splitext(image_name)[0]
        new_name = os.path.join(png_path, filename + ".png").replace("\\", "/")
        new_folder = os.path.dirname(new_name)
        if not os.path.exists(new_folder):
            os.makedirs(new_folder)
        im.save(new_name)


def jpg_to_png_folder(img_folder, png_folder):
    """Convert all jpg files in a folder to png files.

    Args:
        img_folder (str): Path to the folder containing jpg files.
        png_folder (str): Path where the converted png files will be saved.

    Returns:
        Saved png files in the specified folder.
    """
    if not os.path.exists(png_folder):
        os.makedirs(png_folder)

    imgs = [
        os.path.relpath(os.path.join(root, file), img_folder)
        for root, _, files in os.walk(img_folder)
        for file in files
        if (file.endswith(".JPG") or file.endswith(".jpg")) and not file.startswith(".")
    ]

    for img_name in imgs:
        img_name = img_name.replace("\\", "/")
        jpg_to_png(
            img_name, os.path.join(img_folder, img_name).replace("\\", "/"), png_folder
        )
