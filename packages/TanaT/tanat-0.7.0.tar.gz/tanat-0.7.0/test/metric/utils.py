#!/usr/bin/env python3
"""Test utils."""

import numpy as np


def replace_nan_with_value(d, nan_value="NaN"):
    """
    Function to replace all occurrences of np.nan in a dictionary with a specific value.
    """
    return {key: (nan_value if np.isnan(value) else value) for key, value in d.items()}
