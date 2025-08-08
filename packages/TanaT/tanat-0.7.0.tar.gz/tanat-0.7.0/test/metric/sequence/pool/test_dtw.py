#!/usr/bin/env python3
"""Test DTWSequenceMetric."""

import pytest

from tanat.metric.entity.type.hamming.metric import HammingEntityMetric
from tanat.metric.sequence.type.dtw.metric import (
    DTWSequenceMetric,
)
from tanat.metric.sequence.type.dtw.settings import (
    DTWSequenceMetricSettings,
)

from ...utils import replace_nan_with_value


class TestDTWSequenceMetric:
    """
    Test DTWSequenceMetric using different sequence pools.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_collect_as_dict_equivalence_with_snapshot(
        self, sequence_pools, pool_type, snapshot
    ):
        """
        Ensure collect_as_dict gives the same result whether entity metric is passed as object or string.
        Snapshot is used to check the actual content.
        """
        pool = sequence_pools[pool_type]
        # Initialisation with HammingEntityMetric object
        metric_obj = DTWSequenceMetric(
            settings=DTWSequenceMetricSettings(entity_metric=HammingEntityMetric())
        )
        # Initialisation with string "hamming"
        metric_str = DTWSequenceMetric(
            settings=DTWSequenceMetricSettings(entity_metric="hamming")
        )

        # Collect results as dict
        dict_obj = metric_obj.collect_as_dict(pool)
        dict_str = metric_str.collect_as_dict(pool)
        dict_obj = replace_nan_with_value(dict_obj)
        dict_str = replace_nan_with_value(dict_str)
        sorted_dict_obj = dict(sorted(dict_obj.items()))
        sorted_dict_str = dict(sorted(dict_str.items()))

        # Check consistency
        assert sorted_dict_obj == sorted_dict_str
        # Verification via snapshot for both normalized results
        snapshot.assert_match(sorted_dict_obj)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_collect_as_matrix_equivalence_with_snapshot(
        self, sequence_pools, pool_type, snapshot
    ):
        """
        Ensure collect_as_matrix gives the same result whether entity metric is passed as object or string.
        Snapshot is used to check the actual content.
        """
        pool = sequence_pools[pool_type]
        # Initialisation with HammingEntityMetric object
        metric_obj = DTWSequenceMetric(
            settings=DTWSequenceMetricSettings(entity_metric=HammingEntityMetric())
        )
        # Initialisation with string "hamming"
        metric_str = DTWSequenceMetric(
            settings=DTWSequenceMetricSettings(entity_metric="hamming")
        )

        # Collect results as matrix
        pd_matrix_obj = metric_obj.collect_as_matrix(pool)
        pd_matrix_str = metric_str.collect_as_matrix(pool)

        # Verification of equivalence
        assert pd_matrix_obj.equals(pd_matrix_str)
        # Verification via snapshot for both results
        snapshot.assert_match(pd_matrix_obj.to_csv())
