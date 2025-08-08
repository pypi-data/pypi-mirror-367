#!/usr/bin/env python3
"""Test LCPSequenceMetric call method."""

import pytest

from tanat.metric.sequence.type.lcp.metric import (
    LCPSequenceMetric,
)
from tanat.metric.sequence.type.lcp.settings import (
    LCPSequenceMetricSettings,
)


class TestLCPCall:
    """
    Test LCPSequenceMetric call method.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_with_snapshot(self, sequence_pools, pool_type, snapshot):
        """
        Ensure call method gives expected results for LCPSequenceMetric.
        Snapshot is used to check the actual content.
        """
        pool = sequence_pools[pool_type]
        # Initialize LCPSequenceMetric with default settings
        metric = LCPSequenceMetric(settings=LCPSequenceMetricSettings())

        ## -- sequence to compare
        seq_a = pool[2]
        seq_b = pool[3]

        # Call with SequenceMetric object
        value = metric(seq_a, seq_b)
        snapshot.assert_match(value)
