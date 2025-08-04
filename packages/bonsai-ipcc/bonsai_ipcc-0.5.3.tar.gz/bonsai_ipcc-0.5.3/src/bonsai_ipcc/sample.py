import logging

import numpy as np
import pandas as pd

from .uncertainties import monte_carlo, sample_dirichlet

logger = logging.getLogger(__name__)


def create_sample(dfs, constraints=None, size=1000):
    """Add sample to parameter tables.

    For parameter tables in which values are related and constraint, Dirichlet distribution is used for samples.
    For other parameter tables, sample is determined independently using the best fit distribution.

    Argument
    --------
    dfs : dict
        key is name of paramter, value is df
    constraints: dict
        key is name of parameter, value is dict with
            group_py: ["year", "region", "product"]
    size : int
        sample size

    Returns
    -------
    dict of dfs
        revised parameter tables with sample array
    """

    modified_dfs = {}
    for k in dfs.keys():
        df = dfs[k].copy()

        # Use Dirichlet for constraint parameters (values sum up across a level)
        if constraints:
            if k in constraints.keys():
                levels_core = constraints[f"{k}"]["group_by"]
                levels_to_drop = [
                    level for level in df.index.names if level not in levels_core
                ]
                level_to_sum = list(df.index.names)
                levels_not_to_sum = levels_core + ["property"]
                for item in levels_not_to_sum:
                    if item in level_to_sum:
                        level_to_sum.remove(item)
                if len(level_to_sum) != 1:
                    raise ValueError(f"more then one level to sum in '{k}'")
                level_to_sum = level_to_sum[0]

                tmp = np.empty((0, size))
                for coords in df.droplevel(levels_to_drop).index.unique():

                    if "property" in df.index.names:
                        level_values_to_sum = (
                            df.loc[tuple(coords)]
                            .index.get_level_values(level_to_sum)
                            .unique()
                        )
                        default = []
                        max95 = []
                        abs_max = []
                        for l in level_values_to_sum:
                            _df = df.loc[tuple(coords) + (f"{l}",)]
                            if not _df.empty:
                                default.append(
                                    df.loc[
                                        tuple(coords)
                                        + (
                                            f"{l}",
                                            "def",
                                        )
                                    ].value
                                )
                                max95.append(
                                    df.loc[
                                        tuple(coords)
                                        + (
                                            f"{l}",
                                            "max",
                                        )
                                    ].value
                                )
                                abs_max.append(
                                    df.loc[
                                        tuple(coords)
                                        + (
                                            f"{l}",
                                            "abs_max",
                                        )
                                    ].value
                                )
                    sample = sample_dirichlet(default, max95, abs_max, size=size)

                    tmp = np.vstack((tmp, sample))

                for s, coords in enumerate(df.droplevel("property").index.unique()):
                    u = df.loc[tuple(coords) + ("max",)].unit

                    df["value"] = df["value"].astype(object)
                    new_index = df.index.append(
                        pd.MultiIndex.from_tuples(
                            [tuple(coords) + ("sample",)], names=df.index.names
                        )
                    )
                    df = df.reindex(new_index)
                    df.at[tuple(coords) + ("sample",), "value"] = tmp[s]
                    df.at[tuple(coords) + ("sample",), "unit"] = u
                    modified_dfs[f"{k}"] = df
                logger.info(
                    f"Dirichlet distribution used for parameter '{k}' and coords '{coords}'"
                )

        # For other parameters chose best fit
        else:
            for coords in df.droplevel("property").index.unique():
                if "property" in df.index.names:
                    d = df.loc[tuple(coords) + ("def",)].value
                    min_val = df.loc[tuple(coords) + ("min",)].value
                    max_val = df.loc[tuple(coords) + ("max",)].value
                    abs_min = df.loc[tuple(coords) + ("abs_min",)].value
                    abs_max = df.loc[tuple(coords) + ("abs_max",)].value

                    logger.info(
                        f"Uncertainty distribution for parameter '{k}' and coords '{coords}' is:"
                    )
                    tmp = monte_carlo(
                        default=d,
                        min95=min_val,
                        max95=max_val,
                        abs_min=abs_min,
                        abs_max=abs_max,
                        size=size,
                        distribution="check",
                    )
                    u = df.loc[tuple(coords) + ("max",)].unit

                    df["value"] = df["value"].astype(object)
                    new_index = df.index.append(
                        pd.MultiIndex.from_tuples(
                            [tuple(coords) + ("sample",)], names=df.index.names
                        )
                    )
                    df = df.reindex(new_index)

                    df.at[tuple(coords) + ("sample",), "value"] = tmp
                    df.at[tuple(coords) + ("sample",), "unit"] = u
                    modified_dfs[f"{k}"] = df

                else:
                    raise ValueError

    return modified_dfs
