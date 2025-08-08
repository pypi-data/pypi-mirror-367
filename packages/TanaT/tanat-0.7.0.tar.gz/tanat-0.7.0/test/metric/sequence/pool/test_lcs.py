#!/usr/bin/env python3
"""Test LCSSequenceMetric."""

import pytest

from tanat.metric.sequence.type.lcs.metric import (
    LCSSequenceMetric,
)
from tanat.metric.sequence.type.lcs.settings import (
    LCSSequenceMetricSettings,
)

from ...utils import replace_nan_with_value


class TestLCSSequenceMetric:
    """
    Test LCSSequenceMetric using different sequence pools.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_collect_as_dict_with_snapshot(self, sequence_pools, pool_type, snapshot):
        """
        Ensure collect_as_dict gives expected results for LCSSequenceMetric.
        Snapshot is used to check the actual content.
        """
        pool = sequence_pools[pool_type]
        # Initialize LCSSequenceMetric with default settings
        metric = LCSSequenceMetric(settings=LCSSequenceMetricSettings())

        # Collect results as dict
        result_dict = metric.collect_as_dict(pool)
        result_dict = replace_nan_with_value(result_dict)
        sorted_dict = dict(sorted(result_dict.items()))

        # Verification via snapshot
        snapshot.assert_match(sorted_dict)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_collect_as_matrix_with_snapshot(self, sequence_pools, pool_type, snapshot):
        """
        Ensure collect_as_matrix gives expected results for LCSSequenceMetric.
        Snapshot is used to check the actual content.
        """
        pool = sequence_pools[pool_type]
        # Initialize LCSSequenceMetric with default settings
        metric = LCSSequenceMetric(settings=LCSSequenceMetricSettings())

        # Collect results as matrix
        pd_matrix = metric.collect_as_matrix(pool)

        # Verification via snapshot
        snapshot.assert_match(pd_matrix.to_csv())
