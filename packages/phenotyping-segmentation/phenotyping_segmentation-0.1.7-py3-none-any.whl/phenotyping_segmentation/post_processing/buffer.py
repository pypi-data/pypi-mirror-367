# from shapely import Polygon
from shapely.geometry import Polygon


def buffer(bbox, buffer_ratio):
    """Ruturn the bounding box with a buffer area.

    Args:
        bbox: tuple of bounding box of (left, top, width, height)
        ratio: the ratio of buffer width/height to the original bounding box width/height.

    Return:
        Tuple of the buffered bounding box (left, top, width, height)
    """
    left, top, width, height = bbox
    center_x = left + int(width / 2)
    center_y = top + int(height / 2)
    new_left = center_x - int(width * buffer_ratio / 2)
    new_top = center_y - int(height * buffer_ratio / 2)
    if new_left < 0:
        new_left = 0
    if new_top < 0:
        new_top = 0
    return new_left, new_top, int(width * buffer_ratio), int(height * buffer_ratio)


def within_buffer(bbox, bbox2):
    """Check whether any intersection for the two bounding box.

    Parameters
    ----------
    bbox : Tuple
        bounding box with ((left, top, width, height)).
    bbox2 : Tuple
        bounding box with ((left, top, width, height)).

    Returns
    -------
    Boolean data, yes is intersection, no means no intersection.

    """
    polygon = Polygon(
        [
            [bbox[0], bbox[1]],
            [bbox[0], bbox[1] + bbox[3]],
            [bbox[0] + bbox[2], bbox[1] + bbox[3]],
            [bbox[0] + bbox[2], bbox[1]],
        ]
    )
    polygon2 = Polygon(
        [
            [bbox2[0], bbox2[1]],
            [bbox2[0], bbox2[1] + bbox2[3]],
            [bbox2[0] + bbox2[2], bbox2[1] + bbox2[3]],
            [bbox2[0] + bbox2[2], bbox2[1]],
        ]
    )
    return polygon.intersects(polygon2)
