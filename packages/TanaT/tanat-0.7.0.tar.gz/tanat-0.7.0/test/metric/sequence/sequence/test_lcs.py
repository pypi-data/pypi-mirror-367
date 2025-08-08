#!/usr/bin/env python3
"""Test LCSSequenceMetric call method."""

import pytest

from tanat.metric.sequence.type.lcs.metric import (
    LCSSequenceMetric,
)
from tanat.metric.sequence.type.lcs.settings import (
    LCSSequenceMetricSettings,
)


class TestLCSSequenceMetric:
    """
    Test LCSSequenceMetric call method.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_with_snapshot(self, sequence_pools, pool_type, snapshot):
        """
        Ensure call method gives expected results for LCSSequenceMetric.
        Snapshot is used to check the actual content.
        """
        pool = sequence_pools[pool_type]
        # Initialize LCSSequenceMetric with default settings
        metric = LCSSequenceMetric(settings=LCSSequenceMetricSettings())

        ## -- sequence to compare
        seq_a = pool[2]
        seq_b = pool[3]

        # Call with SequenceMetric object
        value = metric(seq_a, seq_b)
        snapshot.assert_match(value)
