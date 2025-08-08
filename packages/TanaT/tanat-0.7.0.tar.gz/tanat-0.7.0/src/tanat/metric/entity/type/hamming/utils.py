# #!/usr/bin/env python3
"""
Utility functions for the Hamming Entity metric.
"""

import logging

import numpy as np

LOGGER = logging.getLogger(__name__)


def get_cost_from_dict(a, b, cost_dict, default_value):
    """Get cost from dictionary with fallback to default value."""
    if cost_dict is None:
        return None
    return float(
        cost_dict.get((a, b))
        or cost_dict.get((b, a))
        or (
            LOGGER.warning(
                "Could not find distance between %s and %s. Using default value.", a, b
            )
            or default_value
        )
    )


def compute_hamming_elementwise(arrays_a, arrays_b):
    """Compute Hamming distance between aligned arrays."""
    mismatch = arrays_a != arrays_b
    return (np.sum(mismatch, axis=1) > 0).astype(float)


def compute_hamming_allpairs(arrays_a, arrays_b):
    """Compute Hamming distance between all possible pairs."""
    n, m = len(arrays_a), len(arrays_b)
    result = np.zeros((n, m))
    for i in range(n):
        result[i] = (arrays_a[i] != arrays_b).any(axis=1).astype(float)
    return result


def pad_to_length(array, target_length, default_value):
    """Pad array to target length with default value."""
    if len(array) >= target_length:
        return array
    padding = np.full((target_length - len(array),) + array.shape[1:], default_value)
    return np.concatenate([array, padding])
