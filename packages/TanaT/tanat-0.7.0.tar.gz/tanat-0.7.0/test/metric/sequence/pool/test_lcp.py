#!/usr/bin/env python3
"""Test LCPSequenceMetric."""

import pytest

from tanat.metric.sequence.type.lcp.metric import (
    LCPSequenceMetric,
)
from tanat.metric.sequence.type.lcp.settings import (
    LCPSequenceMetricSettings,
)

from ...utils import replace_nan_with_value


class TestLCPSequenceMetric:
    """
    Test LCPSequenceMetric using different sequence pools.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_collect_as_dict_with_snapshot(self, sequence_pools, pool_type, snapshot):
        """
        Ensure collect_as_dict gives expected results for LCPSequenceMetric.
        Snapshot is used to check the actual content.
        """
        pool = sequence_pools[pool_type]
        # Initialize LCPSequenceMetric with default settings
        metric = LCPSequenceMetric(settings=LCPSequenceMetricSettings())

        # Collect results as dict
        result_dict = metric.collect_as_dict(pool)
        result_dict = replace_nan_with_value(result_dict)
        sorted_dict = dict(sorted(result_dict.items()))

        # Verification via snapshot
        snapshot.assert_match(sorted_dict)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_collect_as_matrix_with_snapshot(self, sequence_pools, pool_type, snapshot):
        """
        Ensure collect_as_matrix gives expected results for LCPSequenceMetric.
        Snapshot is used to check the actual content.
        """
        pool = sequence_pools[pool_type]
        # Initialize LCPSequenceMetric with default settings
        metric = LCPSequenceMetric(settings=LCPSequenceMetricSettings())

        # Collect results as matrix
        pd_matrix = metric.collect_as_matrix(pool)

        # Verification via snapshot
        snapshot.assert_match(pd_matrix.to_csv())
