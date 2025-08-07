import csv
import os


def write_metadata(crop_paths, input_dir):
    """Write metadata with cropped image path.

    Args:
        crop_paths: a list of the cropped path of each frame;
        input_dir: input dir of this pipeline.

    Returns:
        metadata filename.
    """
    # get all images
    valid_extensions = (".png", ".jpg", ".jpeg", ".tif", ".bmp")
    image_list = [
        os.path.join(path, file).replace("\\", "/")
        for path in crop_paths
        for file in os.listdir(path)
        if file.lower().endswith(valid_extensions)
    ]
    # write csv
    metadata_row = []
    for i in range(len(image_list)):
        image_path_i = image_list[i]
        metadata_row.append([str(i + 1), image_path_i, image_path_i])
    # save csv file
    metadata_file = os.path.join(input_dir, "metadata_tem.csv")
    header = ["image_id", "image_path", "label_colored_path"]
    with open(metadata_file, "w") as csvfile:
        writer = csv.writer(csvfile, lineterminator="\n")
        writer.writerow([g for g in header])
        for x in range(len(metadata_row)):
            writer.writerow(metadata_row[x])
    return metadata_file
