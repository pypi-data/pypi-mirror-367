#!/usr/bin/env python3
"""
Edit distance utils.
"""

import numpy as np


def _process_edit_pair(prepared_pair):
    """Process a single pair of sequences for Edit distance computation."""
    (
        data_a,
        data_b,
        pair_ids,
        distance_computer,
        deletion_cost,
        as_dist,
        norm,
    ) = prepared_pair

    distance = compute_edit(
        data_a,
        data_b,
        distance_computer,
        deletion_cost,
        as_dist,
        norm,
    )
    return pair_ids, distance


# pylint: disable=too-many-arguments
def compute_edit(
    data_a, data_b, entity_metric_func, deletion_cost, as_dist=False, norm=False
):
    """
    Compute the Edit distance between two sequences.

    Args:
        data_a (np.ndarray): First sequence data.
        data_b (np.ndarray): Second sequence data.
        entity_metric_func (callable): Function to compute entity-level distances.
        deletion_cost (float): Cost for deletion/insertion operations.
        as_dist (bool): If True, return distance measure. If False, return similarity.
        norm (bool): Whether to normalize the distance score (only when dist=True).

    Returns:
        float: The Edit distance or similarity score.
    """
    n, m = len(data_a), len(data_b)
    if n == 0 or m == 0:
        return deletion_cost * max(n, m)

    # Compute entity-level distances
    distances = entity_metric_func(data_a, data_b)

    # Initialize distance matrix
    matrix = np.zeros((n + 1, m + 1))
    matrix[0, :] = np.arange(m + 1) * deletion_cost
    matrix[:, 0] = np.arange(n + 1) * deletion_cost

    # Fill the matrix
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            matrix[i, j] = min(
                matrix[i - 1, j - 1] + distances[i - 1, j - 1],  # substitution
                matrix[i - 1, j] + deletion_cost,  # deletion
                matrix[i, j - 1] + deletion_cost,  # insertion
            )

    result = matrix[n, m]

    if as_dist and norm:
        return 1.0 - float(result) / np.sqrt(n * m)
    if as_dist:
        return float(n + m - 2 * result)
    return float(result)
