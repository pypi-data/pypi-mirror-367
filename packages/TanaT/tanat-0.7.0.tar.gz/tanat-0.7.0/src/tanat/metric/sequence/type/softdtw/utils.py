#!/usr/bin/env python3
"""
SoftDtw utils.
"""

import numpy as np


def _process_soft_dtw_pair(prepared_pair):
    """Process a single pair of sequences with SoftDTW."""
    seq_a_array, seq_b_array, pair_ids, distance_computer, gamma = prepared_pair
    distance, matrix = compute_soft_dtw(
        seq_a_array,
        seq_b_array,
        distance_computer,
        gamma,
    )
    return pair_ids, distance, matrix


def _softmin3(a, b, c, gamma):
    """
    Compute softmin of 3 input variables with parameter gamma.
    In the limit case gamma → 0, reduces to hard-min operator.

    Args:
        a (float64): First input variable.
        b (float64): Second input variable.
        c (float64): Third input variable.
        gamma (float64): Regularization parameter.

    Returns:
        float64: Softmin value.
    """
    values = np.array([a, b, c], dtype=np.float64) / -gamma
    max_val = np.max(values)
    softmin_value = -gamma * (np.log(np.sum(np.exp(values - max_val))) + max_val)
    return softmin_value


def compute_soft_dtw(seq_a_array, seq_b_array, entity_metric_func, gamma):
    """
    Compute the SoftDTW (Soft Dynamic Time Warping) distance between two sequences.

    Args:
        seq_a_array (np.ndarray):
            Data array for the first sequence.
        seq_b_array (np.ndarray):
            Data array for the second sequence.
        entity_metric_func (callable):
            Callable that computes the entity metric between two entities.
        gamma (float):
            Regularization parameter for soft-min function.

    Returns:
        Tuple[float, np.ndarray]:
            Returns a tuple of the SoftDTW distance and the complete SoftDTW matrix.

    Raises:
        ValueError: If input sequences are empty.
    """
    if len(seq_a_array) == 0 or len(seq_b_array) == 0:
        raise ValueError("Input sequences cannot be empty")

    m, n = len(seq_a_array), len(seq_b_array)
    distances = entity_metric_func(seq_a_array, seq_b_array)

    # Initialize r_matrix with +inf at borders and 0 at (0,0)
    r_matrix = np.zeros((m + 2, n + 2), dtype=np.float64)
    r_matrix[:-2, 0] = np.finfo("double").max
    r_matrix[0, :-2] = np.finfo("double").max
    r_matrix[0, 0] = 0

    # DP recursion
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            r_matrix[i, j] = distances[i - 1, j - 1] + _softmin3(
                r_matrix[i - 1, j],
                r_matrix[i - 1, j - 1],
                r_matrix[i, j - 1],
                gamma,
            )

    return float(r_matrix[m, n]), r_matrix
