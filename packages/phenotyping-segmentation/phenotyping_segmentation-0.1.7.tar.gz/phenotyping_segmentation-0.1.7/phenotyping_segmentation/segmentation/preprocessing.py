import albumentations as album


def get_preprocessing(preprocessing_fn=None):
    """Construct preprocessing transform.

    Args:
        preprocessing_fn: data normalization function
            (can be specific for each pretrained neural network)

    Return:
        transform: albumentations.Compose
    """
    _transform = []
    if preprocessing_fn:
        _transform.append(album.Lambda(image=preprocessing_fn))
    _transform.append(album.Lambda(image=to_tensor, mask=to_tensor))
    return album.Compose(_transform)


def to_tensor(x, **kwargs):
    return x.transpose(2, 0, 1).astype("float32")


def crop_image(image, true_dimensions):
    """Crop images"""
    return album.CenterCrop(p=1, height=true_dimensions[0], width=true_dimensions[1])(
        image=image
    )
