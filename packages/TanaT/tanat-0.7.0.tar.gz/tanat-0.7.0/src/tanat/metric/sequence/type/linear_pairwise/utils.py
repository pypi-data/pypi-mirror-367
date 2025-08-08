#!/usr/bin/env python3
"""
Linear pairwise utils.
"""


def _process_linear_pair(prepared_pair):
    """Process a single pair for linear pairwise computation."""
    data_a, data_b, pair_ids, distance_computer, agg_fun = prepared_pair
    distances = distance_computer(data_a, data_b)
    return pair_ids, agg_fun(distances)
