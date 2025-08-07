from phenotyping_segmentation.utils.imglist import get_imglist
from tests.fixtures.data import shoot_maize_seg_folder


def test_get_imglist(shoot_maize_seg_folder):
    """Test the imglist function."""
    imgs = get_imglist(shoot_maize_seg_folder)
    assert (
        len(imgs) == 10
    ), "The number of images in the segmentation folder is not correct."
    assert all(img.endswith(".png") for img in imgs), "Not all images are PNG files."
