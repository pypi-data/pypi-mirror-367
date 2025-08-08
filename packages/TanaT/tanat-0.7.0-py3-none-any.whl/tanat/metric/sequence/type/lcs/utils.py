#!/usr/bin/env python3
"""
Longest Common Subsequence utils.
"""

import numpy as np


def compute_lcs(seq_a, seq_b):
    """Compute Longest Common Subsequence between two sequences."""
    start_idx = 0
    a_end = len(seq_a) - 1
    b_end = len(seq_b) - 1

    if a_end < 0 or b_end < 0:
        return 0.0

    def find_matching_prefix():
        idx = 0
        while idx <= a_end and idx <= b_end and np.array_equal(seq_a[idx], seq_b[idx]):
            idx += 1
        return idx

    def find_matching_suffix(start, a_last, b_last):
        count = 0
        while (
            start <= a_last
            and start <= b_last
            and np.array_equal(seq_a[a_last], seq_b[b_last])
        ):
            a_last -= 1
            b_last -= 1
            count += 1
        return count, a_last, b_last

    prefix_length = find_matching_prefix()
    start_idx = prefix_length

    suffix_length, a_end, b_end = find_matching_suffix(start_idx, a_end, b_end)

    if start_idx > a_end or start_idx > b_end:
        return prefix_length + suffix_length

    def compute_middle_section():
        current = np.zeros(b_end - start_idx + 2)
        previous = np.zeros_like(current)

        for i in range(a_end - start_idx + 1):
            for j in range(b_end - start_idx + 1):
                if np.array_equal(seq_a[start_idx + i], seq_b[start_idx + j]):
                    current[j + 1] = previous[j] + 1
                else:
                    current[j + 1] = max(current[j], previous[j + 1])
            previous[:] = current
        return current[-1]

    middle_length = compute_middle_section()
    return middle_length + prefix_length + suffix_length


def _process_lcs_pair(prepared_pair):
    """
    Standalone function for processing a single pair.
    Maintenant reçoit directement les arrays.
    """
    arr_a, arr_b, pair_ids = prepared_pair
    lcss = compute_lcs(arr_a, arr_b)
    return pair_ids, lcss, len(arr_a), len(arr_b)
