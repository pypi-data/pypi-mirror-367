import numpy as np

from scipy.optimize import curve_fit


def func(x, beta):
    """D95 fitting model
    refer to paper: Jackson, R. B., Canadell, J., Ehleringer, J. R., Mooney, H. A.,
    Sala, O. E., & Schulze, E. D. (1996).
    A global analysis of root distributions for terrestrial biomes.
    Oecologia, 108, 389-411.
    """
    return 1 - np.power(beta, x)


def d95_model(nlayer, im_depth, data_pts):
    """Simulate and output the D95 model.

    Args:
        nlayer: the layers to seperate the segmentation images on verticle direction.
        im_depth: depth of the image.
        data_pts: Root pixel locations as an array of shape (n, 2).

    Returns:
        d95 variables:
            beta, beta value of the fitteed curve
            r2, fittness of the curve
            d95_layer, the layer index which greater than 95th percentile of root pixels
    """
    if len(data_pts) > 0:
        # get depth of each layer
        depth_layer = int(im_depth / nlayer)

        # get y locations of root pixels
        data_pts_y = data_pts[:, 1]

        # get the pixel counts for each layer and accumulated counts for each layer
        count_layer = []
        count_sum_layer = []
        # calculate the pixel number of root for each layer
        for j in range(nlayer):
            # get the location of each layer
            lower_bound = j * depth_layer
            upper_bound = (j + 1) * depth_layer
            pixel_per_layer = data_pts_y[
                (data_pts_y >= lower_bound) & (data_pts_y < upper_bound)
            ]
            # get count per layer
            count_per_layer = len(pixel_per_layer)
            count_layer.append(count_per_layer)

            # get accumulated count per layer
            count_layer_sum = sum(count_layer)
            count_sum_layer = np.append(count_sum_layer, count_layer_sum)

        # get accumulated frequency for each layer
        count_layer_sum_frac = count_sum_layer / len(data_pts)

        # get x and y for the power function to calculate beta and r2
        y = count_layer_sum_frac
        x = np.array(list(range(1, nlayer + 1)))

        popt, pcov = curve_fit(func, x, y)
        beta = np.squeeze(popt)
        y_esti = 1 - np.power(popt, x)

        corr_matrix = np.corrcoef(y, y_esti)
        corr = corr_matrix[0, 1]
        r2 = corr**2

        # get 95th layer
        d95_layer = np.where(count_layer_sum_frac > 0.95)[0][0]

    else:
        beta = r2 = d95_layer = np.nan

    return beta, r2, d95_layer
