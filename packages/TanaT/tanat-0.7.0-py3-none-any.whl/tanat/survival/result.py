#!/usr/bin/env python3
"""
Survival analysis results.
"""

from dataclasses import dataclass
import pandas as pd
import numpy as np


@dataclass
class SurvivalResult:
    """Container for survival analysis results."""

    survival_array: np.ndarray
    sequence_ids: list
    endpoint_dates: pd.Series
    t_zeros: pd.Series
    durations: pd.Series
    observation_data: pd.DataFrame
