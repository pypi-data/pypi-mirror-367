#!/usr/bin/env python3
"""
Temporal binning utilities for sequence data.
"""

import pandas as pd
from .granularity import Granularity


def create_time_bins(time_series, granularity):
    """
    Create time bins from a time series.

    Args:
        time_series: pandas Series with datetime values
        granularity: Granularity enum value

    Returns:
        pandas Series with binned datetime values
    """
    granularity = _ensure_granularity(granularity)
    return pd.to_datetime(time_series).dt.floor(granularity.pandas_freq)


def expand_state_periods(data, start_col, end_col, entity_col, granularity):
    """
    Expand state periods to individual time points.

    For state sequences, each state period [start, end] is expanded to
    all time points within that period according to granularity.

    Args:
        data: DataFrame with state data
        start_col: Name of start time column
        end_col: Name of end time column
        entity_col: Name of entity/state column
        granularity: Granularity enum value

    Returns:
        DataFrame with expanded time points
    """
    granularity = _ensure_granularity(granularity)
    expanded_data = []

    for _, row in data.iterrows():
        start_time = pd.to_datetime(row[start_col])
        end_time = pd.to_datetime(row[end_col])

        periods = pd.date_range(
            start=start_time,
            end=end_time,
            freq=granularity.pandas_freq,
        )

        for period in periods:
            expanded_data.append(
                {
                    "time_period": period,
                    "state": row[entity_col],
                }
            )

    return pd.DataFrame(expanded_data)


def _ensure_granularity(granularity):
    """Ensure granularity is a Granularity enum."""
    return Granularity.from_str(granularity)
