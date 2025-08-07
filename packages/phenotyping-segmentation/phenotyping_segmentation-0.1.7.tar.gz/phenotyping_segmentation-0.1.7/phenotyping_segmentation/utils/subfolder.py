import os


def get_subfolders(seg_plant_root_folders):
    seg_plant_subfolders = []
    valid_extensions = (".png", ".jpg", ".jpeg", ".tif", ".bmp")
    for dirpath, dirnames, filenames in os.walk(seg_plant_root_folders):
        if (
            any(fname.lower().endswith(valid_extensions) for fname in filenames)
            and not dirnames
        ):
            seg_plant_subfolders.append(dirpath.replace("\\", "/"))
    return sorted(seg_plant_subfolders)
