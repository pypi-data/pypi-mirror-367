import albumentations as album


def get_validation_augmentation():
    """Validation augmentation"""
    # Add sufficient padding to ensure image is divisible by 32
    test_transform = [
        album.PadIfNeeded(
            min_height=1024,
            min_width=1024,
            p=1,  # always_apply=True,
            border_mode=0,
            value=(0, 0, 0),
        ),
    ]
    return album.Compose(test_transform)
