#!/usr/bin/env python3
"""
Longest Common Prefix utils.
"""

import numpy as np


def compute_lcp(seq_a, seq_b):
    """Compute Longest Common Prefix length."""
    min_len = min(len(seq_a), len(seq_b))
    for idx in range(min_len):
        if not np.array_equal(seq_a[idx], seq_b[idx]):
            return idx
    return min_len


def _process_lcp_pair(prepared_pair):
    arr_a, arr_b, pair_ids = prepared_pair
    lcp = compute_lcp(arr_a, arr_b)
    return pair_ids, lcp, len(arr_a), len(arr_b)
