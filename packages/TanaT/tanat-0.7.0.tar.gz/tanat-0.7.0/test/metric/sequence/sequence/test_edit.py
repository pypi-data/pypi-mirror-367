#!/usr/bin/env python3
"""Test LCSSequenceMetric call method."""

import pytest

from tanat.metric.entity.type.hamming.metric import HammingEntityMetric
from tanat.metric.sequence.type.edit.metric import (
    EditSequenceMetric,
)
from tanat.metric.sequence.type.edit.settings import (
    EditSequenceMetricSettings,
)

from ...utils import replace_nan_with_value


class TestEditCall:
    """
    Test EditSequenceMetric call method.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_equivalence_with_snapshot(self, sequence_pools, pool_type, snapshot):
        """
        Ensure call methode gives the same result whether entity metric is passed as object or string.
        Snapshot is used to check the actual content.
        """
        pool = sequence_pools[pool_type]
        # Initialisation with HammingEntityMetric object
        metric_obj = EditSequenceMetric(
            settings=EditSequenceMetricSettings(entity_metric=HammingEntityMetric())
        )
        # Initialisation with string "hamming"
        metric_str = EditSequenceMetric(
            settings=EditSequenceMetricSettings(entity_metric="hamming")
        )

        ## -- sequence to compare
        seq_a = pool[2]
        seq_b = pool[3]

        # Call with SequenceMetric object
        value_obj = metric_obj(seq_a, seq_b)
        # Call with string
        value_str = metric_str(seq_a, seq_b)
        # Check consistency
        assert value_obj == value_str
        snapshot.assert_match(value_obj)
