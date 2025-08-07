import numpy as np
import pandas as pd


def get_statistics(filtered_data, prefix):
    """Get startstics function.

    Args:
        filtered_data: filtered traits.
        prefix: trait name

    Returns:
        a list with statistics.
    """
    if prefix is None:
        prefix = ""

    if len(filtered_data) == 0 or np.isnan(filtered_data).all():
        return {
            f"{prefix}min": np.nan,
            f"{prefix}max": np.nan,
            f"{prefix}mean": np.nan,
            f"{prefix}median": np.nan,
            f"{prefix}std": np.nan,
            f"{prefix}p5": np.nan,
            f"{prefix}p25": np.nan,
            f"{prefix}p75": np.nan,
            f"{prefix}p95": np.nan,
        }
    else:
        return {
            f"{prefix}min": np.nanmin(filtered_data),
            f"{prefix}max": np.nanmax(filtered_data),
            f"{prefix}mean": np.nanmean(filtered_data),
            f"{prefix}median": np.nanmedian(filtered_data),
            f"{prefix}std": np.nanstd(filtered_data),
            f"{prefix}p5": np.nanpercentile(filtered_data, 5),
            f"{prefix}p25": np.nanpercentile(filtered_data, 25),
            f"{prefix}p75": np.nanpercentile(filtered_data, 75),
            f"{prefix}p95": np.nanpercentile(filtered_data, 95),
        }


def get_statistics_df(traits_df, group_index, summary_df):
    """Get startstics of one plant with all frames.

    Args:
        get_statistics_df: traits of one plant with all frames;
        group_index: index to group for statistics calculation;
        summary_df: statistic summary of previous plants;

    Returns:
        a dataframe with statistics of plants.
    """
    plant_df = traits_df.groupby(group_index)
    for name, group in plant_df:
        data_new = pd.DataFrame([{"plant": name}])

        for column in group.columns[2:]:
            filtered = group[column]
            prefix = column + "_"
            traits_summary = get_statistics(filtered, prefix)
            data_new = pd.concat([data_new, pd.DataFrame([traits_summary])], axis=1)
        summary_df = pd.concat([summary_df, data_new])
    return summary_df
