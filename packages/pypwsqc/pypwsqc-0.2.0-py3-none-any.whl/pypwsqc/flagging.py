"""A collection of functions for flagging problematic time steps."""

from __future__ import annotations

import numpy as np
import numpy.typing as npt
import pandas as pd
import xarray as xr


def fz_filter(
    ds_pws: npt.NDArray[np.float64],
    nint: npt.NDArray[np.float64],
    n_stat: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    """Faulty Zeros Filter.

    This function applies the FZ filter from the R package PWSQC.
    The flag 1 means, a faulty zero has been detected. The flag -1
    means that no flagging was done because evaluation cannot be
    performed for the first `nint` values.

    Note that this code here is derived from the Python translation,
    done by Niek van Andel, of the original R code from Lotte de Vos.
    The Python code stems from here https://github.com/NiekvanAndel/QC_radar.
    Also note that the correctness of the Python code has not been
    verified and not all feature of the R implementation might be there.

    Parameters
    ----------
    pws_data
        The rainfall time series of the PWS that should be flagged
    reference
        The rainfall time series of the reference, which can be e.g.
        the median of neighboring PWS data.
    nint : optional
        The number of subsequent data points which have to be zero, while
        the reference has values larger than zero, to set the flag for
        this data point to 1.

    Returns
    -------
    npt.NDArray
        time series of flags
    """
    pws_data = ds_pws.rainfall
    nbrs_not_nan = ds_pws.nbrs_not_nan
    reference = ds_pws.reference

    # find first rainfall observation in each time series
    first_non_nan_index = ds_pws["rainfall"].notnull().argmax(dim="time")  # noqa: PD004

    # Create a mask that is True up to the first valid
    # index for each station, False afterward
    mask = xr.DataArray(
        np.arange(ds_pws.sizes["time"]), dims="time"
    ) < first_non_nan_index.broadcast_like(ds_pws["rainfall"])

    # initialize arrays
    sensor_array = np.zeros_like(pws_data)
    ref_array = np.zeros_like(pws_data)
    fz_array = np.zeros_like(pws_data)

    # Wet timestep at each station
    sensor_array[np.where(pws_data > 0)] = 1

    # Dry timestep at each station
    sensor_array[np.where(pws_data == 0)] = 0

    # Wet timesteps of the reference
    ref_array[np.where(reference > 0)] = 1

    for i in np.arange(len(pws_data.id.data)):
        for j in np.arange(len(pws_data.time.data)):
            if j < nint:
                fz_array[i, j] = -1
            elif sensor_array[i, j] > 0:
                fz_array[i, j] = 0
            elif fz_array[i, j - 1] == 1:
                fz_array[i, j] = 1
            elif (np.sum(sensor_array[i, j - nint : j + 1]) > 0) or (
                np.sum(ref_array[i, j - nint : j + 1]) < nint + 1
            ):
                fz_array[i, j] = 0
            else:
                fz_array[i, j] = 1

    fz_array = fz_array.astype(int)
    fz_flag = xr.where(nbrs_not_nan < n_stat, -1, fz_array)

    # add to dataset
    ds_pws["fz_flag"] = fz_flag

    # set fz_flag to -1 up to the first valid rainfall observation
    ds_pws["fz_flag"] = ds_pws["fz_flag"].where(~mask, -1)

    # check if last nint timesteps are NaN in rolling window
    nan_in_last_nint = (
        ds_pws["rainfall"].rolling(time=nint, center=True).construct("window_dim")
    )
    all_nan_in_window = nan_in_last_nint.isnull().all(dim="window_dim")

    # Apply the mask to set fz_flag to -1 where the condition is met
    ds_pws["fz_flag"] = ds_pws["fz_flag"].where(~all_nan_in_window, -1)

    return ds_pws


def hi_filter(
    ds_pws: npt.NDArray[np.float64],
    hi_thres_a: npt.NDArray[np.float64],
    hi_thres_b: npt.NDArray[np.float64],
    nint: npt.NDArray[np.float64],
    n_stat=npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    """High Influx filter.

    This function applies the HI filter from the R package PWSQC,
    flagging unrealistically high rainfall amounts.

    The Python code has been translated from the original R code,
    to be found here: https://github.com/LottedeVos/PWSQC/tree/master/R.

    The function returns an array with zeros, ones or -1 per time step
    and station.
    The flag 0 means that no high influx has been detected.
    The flag 1 means that high influx has been detected.
    The flag -1 means that no flagging was done because not enough
    neighbouring stations are reporting rainfall to make a reliable
    evaluation.

    Parameters
    ----------
    pws_data
        The rainfall time series of the PWS that should be flagged
    nbrs_not_nan
        Number of neighbouring stations reporting rainfall
    reference
        The rainfall time series of the reference, which can be e.g.
        the median of neighboring stations
    hi_thres_a
        threshold for median rainfall of neighbouring stations [mm]
    hi_thres_b
        upper rainfall limit [mm]
    n_stat
        threshold for number of neighbours reporting rainfall

    Returns
    -------
    npt.NDArray
        time series of flags
    """
    # find first rainfall observation in each time series
    first_non_nan_index = ds_pws["rainfall"].notnull().argmax(dim="time")  # noqa: PD004

    # Create a mask that is True up to the first
    # valid index for each station, False afterward
    mask = xr.DataArray(
        np.arange(ds_pws.sizes["time"]), dims="time"
    ) < first_non_nan_index.broadcast_like(ds_pws["rainfall"])

    condition1 = (ds_pws.reference < hi_thres_a) & (ds_pws.rainfall > hi_thres_b)
    condition2 = (ds_pws.reference >= hi_thres_a) & (
        ds_pws.rainfall > ds_pws.reference * hi_thres_b / hi_thres_a
    )

    hi_array = (condition1 | condition2).astype(int)

    hi_flag = xr.where(ds_pws.nbrs_not_nan < n_stat, -1, hi_array)

    # add to dataset
    ds_pws["hi_flag"] = hi_flag

    # set hi_flag to -1 up to the first valid rainfall observation
    ds_pws["hi_flag"] = ds_pws["hi_flag"].where(~mask, -1)

    # check if last nint timesteps are NaN in rolling window
    nan_in_last_nint = (
        ds_pws["rainfall"].rolling(time=nint, center=True).construct("window_dim")
    )
    all_nan_in_window = nan_in_last_nint.isnull().all(dim="window_dim")

    # Apply the mask to set hi_flag to -1 where the condition is met
    ds_pws["hi_flag"] = ds_pws["hi_flag"].where(~all_nan_in_window, -1)

    return ds_pws


def so_filter_one_station(da_station, da_neighbors, evaluation_period, mmatch):
    """Support function to Station Outlier filter.

    Parameters
    ----------
    da_station
        rainfall time series of evaluated station.
    da_neighbors
        rainfall time series of neighboring stations.
    evaluation_period
        length of (rolling) window for correlation calculation
        [timesteps]
    mmatch
        threshold for number of matching rainy intervals in
        evaluation period [timesteps]

    Returns
    -------
    npt.NDArray
        number of neighbors with enough wet time steps
    """
    # rolling pearson correlation
    s_station = da_station.to_series()
    s_neighbors = da_neighbors.to_series()
    corr = s_station.rolling(evaluation_period, min_periods=1).corr(s_neighbors)
    ds = xr.Dataset.from_dataframe(pd.DataFrame({"corr": corr}))

    # create dataframe of neighboring stations
    df_nbrs = da_neighbors.to_dataframe()
    df_nbrs = df_nbrs["rainfall"].unstack("id")  # noqa: PD010

    # boolean arrays - True if a rainy time step, False if 0 or NaN.
    rainy_timestep_at_nbrs = df_nbrs > 0

    # rolling sum of number of rainy timesteps in
    # last evaluation_period period, per neighbor.
    wet_timesteps_last_evaluation_period_period = rainy_timestep_at_nbrs.rolling(
        evaluation_period, min_periods=1
    ).sum()

    # per time step and neighbor, does the nbr have more than
    # mmatch wet time steps in the last evaluation_period period? (true/false)
    enough_matches_per_nbr = wet_timesteps_last_evaluation_period_period > mmatch

    # summing how many neighbors that have enough matches per time step
    nr_nbrs_with_enough_matches = enough_matches_per_nbr.sum(axis=1)

    ds["matches"] = xr.DataArray.from_series(nr_nbrs_with_enough_matches)

    return ds


def so_filter(
    ds_pws: npt.NDArray[np.float64],
    distance_matrix: npt.NDArray[np.float64],
    evaluation_period: npt.NDArray[np.float64],
    mmatch: npt.NDArray[np.float64],
    gamma: npt.NDArray[np.float64],
    n_stat=npt.NDArray[np.float64],
    max_distance=npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    """Station Outlier filter.

    This function applies the SO filter from the R package PWSQC,
    flagging nonsensical rainfall measurements for a specific location.

    The Python code has been translated from the original R code,
    to be found here: https://github.com/LottedeVos/PWSQC/tree/master/R.

    In its original implementation, any interval with at least `mrain`
    intervals of nonzero rainfall measurements is evaluated.
    In this implementation, only a fixed rolling window of `evaluation_period`
    intervals is evaluated.

    The function returns an array with zeros, ones or -1 per time step
    and station.
    The flag 0 means that no station outlier has been detected.
    The flag 1 means that a station outlier has been detected.
    The flag -1 means that no flagging was done because not enough
    neighbouring stations are reporting rainfall to make a reliable
    evaluation or that the previous evaluation_period time steps was dry.

    Parameters
    ----------
    ds_pws
        xarray data set
    nbrs_not_nan
        Number of neighbouring stations reporting rainfall
    evaluation_period
        length of (rolling) window for correlation calculation
        [timesteps]
    mmatch
        threshold for number of matching rainy intervals in
        evaluation period [timesteps]
    gamma
        threshold for rolling median pearson correlation [-]
    n_stat
        threshold for number of neighbours reporting rainfall
    max_distance
        considered range around each station [m]

    Returns
    -------
    npt.NDArray
        Time series of flags.
    """
    # For each station (ID), get the index of the first non-NaN rainfall value
    first_non_nan_index = ds_pws["rainfall"].notnull().argmax(dim="time")  # noqa: PD004

    for i in range(len(ds_pws.id)):
        ds_station = ds_pws.isel(id=i)
        pws_id = ds_station.id.to_numpy()

        # picking stations within max_distnance, excluding itself,
        # for the whole duration of the time series
        neighbor_ids = distance_matrix.id.data[
            (distance_matrix.sel(id=pws_id) < max_distance)
            & (distance_matrix.sel(id=pws_id) > 0)
        ]

        # create data set for neighbors
        ds_neighbors = ds_pws.sel(id=neighbor_ids)

        # if there are no observations in the time series, filter
        # cannot be applied to the whole time series
        # or if there are not enough stations nearby,
        # filter cannot be applied to the whole time series
        if ds_pws.rainfall.sel(id=pws_id).isnull().all() or (
            len(neighbor_ids) < n_stat
        ):
            ds_pws.so_flag[i, :] = -1
            ds_pws.median_corr_nbrs[i, :] = -1
            continue

        # run so-filter
        ds_so_filter = so_filter_one_station(
            ds_station.rainfall, ds_neighbors.rainfall, evaluation_period, mmatch
        )

        median_correlation = ds_so_filter.corr.median(dim="id", skipna=True)
        ds_pws.median_corr_nbrs[i] = median_correlation

        so_array = (median_correlation < gamma).astype(int)

        # filter can not be applied if less than n_stat neighbors have enough matches
        ds_pws.so_flag[i] = xr.where(ds_so_filter.matches < n_stat, -1, so_array)

        # Set so_flag to -1 up to first valid index
        first_valid_time = first_non_nan_index[i].item()
        ds_pws["so_flag"][i, :first_valid_time] = -1

        # disregard warm up period
        ds_pws.so_flag[
            i, first_valid_time : (first_valid_time + evaluation_period)
        ] = -1

    return ds_pws
