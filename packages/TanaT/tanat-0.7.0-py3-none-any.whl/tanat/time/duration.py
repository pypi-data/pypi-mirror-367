#!/usr/bin/env python3
"""
Duration calculation utilities.
"""

import pandas as pd
from dateutil.rrule import rrule, MONTHLY, YEARLY
from .granularity import Granularity


def calculate_duration_from_series(start_series, end_series, granularity):
    """
    Calculate durations for pandas Series of start and end dates.

    Args:
        start_series: Series of start dates/timestamps
        end_series: Series of end dates/timestamps
        granularity: Target granularity for calculations

    Returns:
        Series of durations in the specified granularity
    """
    granularity = _ensure_granularity(granularity)

    if len(start_series) != len(end_series):
        raise ValueError("Start and end series must have the same length")

    if granularity is Granularity.UNIT:
        return end_series - start_series

    # Vectorized operations for simple units
    if granularity in [Granularity.HOUR, Granularity.DAY, Granularity.WEEK]:
        delta = end_series - start_series
        return _vectorized_duration_methods[granularity](delta)

    # Individual calculations for calendar units
    return pd.Series(
        [
            calculate_duration(start, end, granularity)
            for start, end in zip(start_series, end_series)
        ]
    )


def calculate_duration(start_date, end_date, granularity):
    """
    Calculate exact duration between two dates in specified granularity.
    Takes into account actual calendar durations (leap years, varying
    month lengths).

    Args:
        start_date: Start date/timestamp
        end_date: End date/timestamp
        granularity: Target granularity

    Returns:
        Duration in the specified granularity
    """
    granularity = _ensure_granularity(granularity)
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)

    if start > end:
        start, end = end, start

    duration_methods = {
        Granularity.HOUR: _hours_duration,
        Granularity.DAY: _days_duration,
        Granularity.WEEK: _weeks_duration,
        Granularity.MONTH: _months_duration,
        Granularity.YEAR: _years_duration,
        Granularity.UNIT: lambda start, end: end - start,
    }

    if granularity not in duration_methods:
        raise ValueError(f"Unsupported granularity: {granularity}")

    return duration_methods[granularity](start, end)


def _hours_duration(start, end):
    """Calculate exact hours between dates."""
    delta = end - start
    return delta.total_seconds() / 3600


def _days_duration(start, end):
    """Calculate exact days between dates."""
    delta = end - start
    return delta.total_seconds() / (24 * 3600)


def _weeks_duration(start, end):
    """Calculate exact weeks between dates."""
    delta = end - start
    return delta.total_seconds() / (7 * 24 * 3600)


def _months_duration(start, end):
    """
    Calculate exact months between dates.
    Uses rrule to count actual months and handles partial months.
    """
    # Count full months
    full_months = (
        len(list(rrule(MONTHLY, dtstart=start.replace(day=1), until=end))) - 1
    )  # -1 because we don't count the start month

    # Handle partial months at start and end
    start_fraction = (start.days_in_month - start.day + 1) / start.days_in_month
    end_fraction = end.day / end.days_in_month

    return full_months + start_fraction + end_fraction


def _years_duration(start, end):
    """
    Calculate exact years between dates.
    Uses rrule to count actual years and handles leap years.
    """
    # Count full years
    full_years = len(
        list(rrule(YEARLY, dtstart=start.replace(month=1, day=1), until=end))
    )

    # Handle partial years
    start_days = (pd.Timestamp(f"{start.year}-12-31") - start).days + 1
    end_days = (end - pd.Timestamp(f"{end.year}-01-01")).days + 1

    start_fraction = start_days / (366 if start.is_leap_year else 365)
    end_fraction = end_days / (366 if end.is_leap_year else 365)

    return full_years + start_fraction + end_fraction


def _ensure_granularity(granularity):
    """Ensure granularity is a Granularity enum."""
    if isinstance(granularity, str):
        return Granularity.from_str(granularity)
    return granularity


# Vectorized methods for performance
_vectorized_duration_methods = {
    Granularity.HOUR: lambda delta: delta.dt.total_seconds() / 3600,
    Granularity.DAY: lambda delta: delta.dt.total_seconds() / (24 * 3600),
    Granularity.WEEK: lambda delta: delta.dt.total_seconds() / (7 * 24 * 3600),
}
