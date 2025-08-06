"""Various methods used to compute model evaluation metrics."""
from typing import Callable
import pandas as pd
import numpy as np
import numpy.typing as npt
from arch.bootstrap import StationaryBootstrap, optimal_block_length
from numba import float64, guvectorize

@guvectorize([(float64[:], float64[:], float64[:])], "(n),(n)->()")
def nash_sutcliffe_efficiency(
    y_true: npt.NDArray[np.float64],
    y_pred: npt.NDArray[np.float64],
    result: npt.NDArray[np.float64]
    ) -> None:
    """
    Numba compatible implementation of Nash-Sutcliffe Model Efficiency.
        
    Parameters
    ----------
    y_true: NDArray[np.float64], required
        Ground truth (correct) target values, also called observations, measurements, or observed values.
    y_pred: NDArray[np.float64], required
        Estimated target values, also called simulations, forecasts, or modeled values.
    result: NDArray[np.float64], required
        Stores scalar result.
        
    Returns
    -------
    None
    """
    variance = np.sum((y_true - np.mean(y_true)) ** 2.0)
    if variance == 0:
        result[0] = np.nan
        return
    result[0] = 1.0 - np.sum((y_true - y_pred) ** 2.0) / variance

@guvectorize([(float64[:], float64[:], float64[:])], "(n),(n)->()")
def relative_mean_bias(
    y_true: npt.NDArray[np.float64],
    y_pred: npt.NDArray[np.float64],
    result: npt.NDArray[np.float64]
    ) -> None:
    """
    Numba and polars compatible implementation of signed mean relative bias.
    Also called, mean relative error or fractional bias.
        
    Parameters
    ----------
    y_true: NDArray[np.float64], required
        Ground truth (correct) target values, also called observations, measurements, or observed values.
    y_pred: NDArray[np.float64], required
        Estimated target values, also called simulations or modeled values.
    result: NDArray[np.float64], required
        Stores scalar result.
        
    Returns
    -------
    None
    """
    total = np.sum(y_true)
    if total == 0.0:
        result[0] = np.nan
        return
    result[0] = np.sum(y_pred - y_true) / np.sum(y_true)

@guvectorize([(float64[:], float64[:], float64[:])], "(n),(n)->()")
def pearson_correlation_coefficient(
    y_true: npt.NDArray[np.float64],
    y_pred: npt.NDArray[np.float64],
    result: npt.NDArray[np.float64]
    ) -> None:
    """
    Numba and polars compatible implementation of the Pearson correlation
    coefficient.
        
    Parameters
    ----------
    y_true: NDArray[np.float64], required
        Ground truth (correct) target values, also called observations, measurements, or observed values.
    y_pred: NDArray[np.float64], required
        Estimated target values, also called simulations or modeled values.
    result: NDArray[np.float64], required
        Stores scalar result.
        
    Returns
    -------
    None
    """
    y_true_dev = y_true - np.mean(y_true)
    y_pred_dev = y_pred - np.mean(y_pred)
    num = np.sum(y_true_dev * y_pred_dev)
    den = (
        np.sqrt(np.sum(y_true_dev ** 2)) *
        np.sqrt(np.sum(y_pred_dev ** 2))
        )
    if den == 0:
        result[0] = np.nan
        return
    result[0] = num / den

@guvectorize([(float64[:], float64[:], float64[:])], "(n),(n)->()")
def relative_standard_deviation(
    y_true: npt.NDArray[np.float64],
    y_pred: npt.NDArray[np.float64],
    result: npt.NDArray[np.float64]
    ) -> None:
    """
    Numba and polars compatible implementation of relative standard deviation,
    required to compute Kling-Gupta Model Efficiency.
        
    Parameters
    ----------
    y_true: NDArray[np.float64], required
        Ground truth (correct) target values, also called observations, measurements, or observed values.
    y_pred: NDArray[np.float64], required
        Estimated target values, also called simulations or modeled values.
    result: NDArray[np.float64], required
        Stores scalar result.
        
    Returns
    -------
    None
    """
    std_dev = np.std(y_true)
    if std_dev == 0:
        result[0] = np.nan
        return
    result[0] = np.std(y_pred) / std_dev

@guvectorize([(float64[:], float64[:], float64[:])], "(n),(n)->()")
def relative_mean(
    y_true: npt.NDArray[np.float64],
    y_pred: npt.NDArray[np.float64],
    result: npt.NDArray[np.float64]
    ) -> None:
    """
    Numba and polars compatible implementation of relative mean,
    required to compute Kling-Gupta Model Efficiency.
        
    Parameters
    ----------
    y_true: NDArray[np.float64], required
        Ground truth (correct) target values, also called observations, measurements, or observed values.
    y_pred: NDArray[np.float64], required
        Estimated target values, also called simulations or modeled values.
    result: NDArray[np.float64], required
        Stores scalar result.
        
    Returns
    -------
    None
    """
    mean = np.mean(y_true)
    if mean == 0:
        result[0] = np.nan
        return
    result[0] = np.mean(y_pred) / mean

@guvectorize([(float64[:], float64[:], float64[:])], "(n),(n)->()")
def kling_gupta_efficiency(
    y_true: npt.NDArray[np.float64],
    y_pred: npt.NDArray[np.float64],
    result: npt.NDArray[np.float64]
    ) -> None:
    """Returns an expression used to add a 'kling_gupta_efficiency' column to a dataframe."""
    correlation = np.array([0.0], dtype=np.float64)
    pearson_correlation_coefficient(y_true, y_pred, correlation)
    rel_var = np.array([0.0], dtype=np.float64)
    relative_standard_deviation(y_true, y_pred, rel_var)
    rel_mean = np.array([0.0], dtype=np.float64)
    relative_mean(y_true, y_pred, rel_mean)
    result[0] = (1.0 - np.sqrt(
        ((correlation[0] - 1.0)) ** 2.0 + 
        ((rel_var[0] - 1.0)) ** 2.0 + 
        ((rel_mean[0] - 1.0)) ** 2.0
        ))

METRIC_FUNCTIONS: dict[str, Callable[[npt.NDArray[np.float64], npt.NDArray[np.float64]], npt.NDArray[np.float64]]] = {
    "nash_sutcliffe_efficiency": nash_sutcliffe_efficiency,
    "relative_mean_bias": relative_mean_bias,
    "pearson_correlation_coefficient": pearson_correlation_coefficient,
    "relative_mean": relative_mean,
    "relative_standard_deviation": relative_standard_deviation,
    "kling_gupta_efficiency": kling_gupta_efficiency
}
"""Metrics to compute."""

SUFFIXES: list[str] = ["_point", "_lower", "_upper"]
"""Metric field suffixes."""

METRIC_FIELDS: list[str] = [k+s for k in METRIC_FUNCTIONS.keys() for s in SUFFIXES]
"""Metric field names."""

def bootstrap_metrics(
    data: pd.DataFrame,
    minimum_sample_size: int = 30,
    minimum_mean: float = 0.01,
    minimum_variance: float = 0.000025
    ) -> pd.Series:
    y_true = data["observed"].to_numpy(dtype=np.float64)
    y_pred = data["predicted"].to_numpy(dtype=np.float64)
    sample_size = data["observed"].count()

    results = []
    for _, func in METRIC_FUNCTIONS.items():
        # TODO check for nan?

        # Point estimates
        point_estimate = func(
            y_true, 
            y_pred
            )

        # Low sample size
        if sample_size < minimum_sample_size:
            results.append(np.asarray([point_estimate, np.nan, np.nan]))
            continue
        
        # Mostly zero values
        if np.mean(y_true) < minimum_mean:
            results.append(np.asarray([point_estimate, np.nan, np.nan]))
            continue
        
        # Nearly constant values
        if np.var(y_true) < minimum_variance:
            results.append(np.asarray([point_estimate, np.nan, np.nan]))
            continue
        
        # Optimal block size
        max_value = np.max(y_true) * 1.01
        normalized = y_true / max_value
        block_size = optimal_block_length(normalized)["stationary"][0]
        if np.isnan(block_size):
            block_size = 1
        else:
            block_size = max(1, int(block_size))
        
        # Bootstrap confidence interval for each metric
        indices = np.arange(y_true.size)
        bs = StationaryBootstrap(
            block_size,
            indices,
            seed=2025
            )
        posterior = []
        for samples in bs.bootstrap(1000):
            # Certain functions may need additional error checks
            idx = samples[0][0]
            posterior.append(func(y_true[idx], y_pred[idx]))
        ci = np.quantile(posterior, [0.025, 0.975])
        results.append(np.concatenate(([point_estimate], ci)))
    s = pd.Series(
        np.concatenate(results),
        index=METRIC_FIELDS
    )
    s["sample_size"] = sample_size
    s["start_date"] = data["value_time"].min()
    s["end_date"] = data["value_time"].max()
    s["nwm_feature_id"] = data["nwm_feature_id"].iloc[0]
    s["usgs_site_code"] = data["usgs_site_code"].iloc[0]
    if "lead_time_hours_min" in data:
        s["lead_time_hours_min"] = data["lead_time_hours_min"].min()
    return s
