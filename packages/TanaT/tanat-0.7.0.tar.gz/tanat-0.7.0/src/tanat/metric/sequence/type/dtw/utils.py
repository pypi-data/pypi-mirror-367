#!/usr/bin/env python3
"""
DTW utils.
"""

import numpy as np


def _process_dtw_pair(prepared_pair):
    (
        seq_a_arrays,
        seq_b_arrays,
        pair_ids,
        distance_computer,
        tc_param,
        sc_param,
        compute_matrix,
    ) = prepared_pair

    distance, matrix = compute_dtw(
        seq_a_arrays,
        seq_b_arrays,
        distance_computer,
        tc_param,
        sc_param,
        compute_matrix=compute_matrix,
    )
    return pair_ids, distance, matrix


def _init_dtw_params(data_a, data_b, sc_param):
    n, m = len(data_a), len(data_b)
    if n == 0 or m == 0:
        raise ValueError("Input sequences cannot be empty")

    if sc_param is not None:
        sc_param = min(sc_param, min(n, m) - 1)
        n_sc, m_sc = n - sc_param, m - sc_param
    else:
        n_sc, m_sc = n, m
    return n, m, n_sc, m_sc


# pylint: disable=too-many-arguments, too-many-locals
def compute_dtw(
    seq_a_arrays,
    seq_b_arrays,
    entity_metric_func,
    tc_param=None,
    sc_param=None,
    *,
    compute_matrix=False,
):
    """
    Compute the DTW (Dynamic Time Warping) distance between two sequences.

    Args:
        seq_a_arrays (Tuple[np.ndarray, np.ndarray]):
            Tuple of data and dates arrays for the first sequence.
        seq_b_arrays (Tuple[np.ndarray, np.ndarray]):
            Tuple of data and dates arrays for the second sequence.
        entity_metric_func (callable):
            Callable that computes the entity metric between two entities.
        tc_param (Optional[np.timedelta64]):
            Time constraint parameter. If not None, restricts the warping path
            to stay within a band around the diagonal defined by this parameter.
        sc_param (Optional[int]):
            Sakoe-Chiba band width parameter. If not None, restricts the warping
            path to stay within a band around the diagonal defined by this parameter.
        compute_matrix (bool, optional):
            If True, computes and returns the complete DTW matrix. Defaults to False.

    Returns:
        float or Tuple[float, np.ndarray]:
            If compute_matrix is False, returns the DTW distance as a float. If
            compute_matrix is True, returns a tuple of the DTW distance and the
            complete DTW matrix.
    """

    def _compute_transition_cost(dtw_matrix, i, j, entity_dist):
        """Compute the transition cost between two cells in the DTW matrix"""
        return entity_dist + min(
            dtw_matrix[i - 1 if compute_matrix else 0, j],
            dtw_matrix[i if compute_matrix else 1, j - 1],
            dtw_matrix[i - 1 if compute_matrix else 0, j - 1],
        )

    def _is_valid_time_constraint(i, j):
        """Check if the time constraint is valid for the given indices"""
        return tc_param is None or abs(dates_a[i - 1] - dates_b[j - 1]) <= tc_param

    data_a, dates_a = seq_a_arrays
    data_b, dates_b = seq_b_arrays
    n, m, n_sc, m_sc = _init_dtw_params(data_a, data_b, sc_param)
    distances = entity_metric_func(data_a, data_b)

    dtw = np.full((n + 1 if compute_matrix else 2, m + 1), np.inf)
    dtw[0, 0] = 0.0

    for i in range(1, n + 1):
        j_start, j_end = max(1, i - n_sc + 1), min(m, i + m_sc - 1) + 1
        for j in range(j_start, j_end):
            if _is_valid_time_constraint(i, j):
                dtw[i if compute_matrix else 1, j] = _compute_transition_cost(
                    dtw, i, j, distances[i - 1, j - 1]
                )
                if not compute_matrix:
                    dtw[0, j] = dtw[1, j]

        if not compute_matrix:
            dtw[1, :] = np.inf

    final_distance = float(dtw[n if compute_matrix else 0, m])
    return final_distance, dtw
