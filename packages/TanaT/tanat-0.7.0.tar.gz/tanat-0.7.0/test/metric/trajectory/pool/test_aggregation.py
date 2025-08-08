#!/usr/bin/env python3
"""Test TrajectoryMetric."""

import pytest

from tanat.metric.trajectory.type.aggregation.metric import (
    AggregationTrajectoryMetric,
)
from tanat.metric.trajectory.type.aggregation.settings import (
    AggregationTrajectoryMetricSettings,
)
from tanat.metric.sequence.base.metric import SequenceMetric

from ...utils import replace_nan_with_value


class TestAggregationTrajectoryMetric:
    """
    Test AggregationTrajectoryMetric on a trajectory pool.
    """

    @pytest.mark.parametrize(
        "sequence_metric", ["linearpairwise", "softdtw", "lcs", "lcp", "edit", "dtw"]
    )
    def test_collect_as_dict_equivalence_with_snapshot(
        self, trajectory_pool, sequence_metric, snapshot
    ):
        """
        Ensure collect_as_dict gives the same result whether sequence metric is passed as object or string.
        Snapshot is used to check the actual content.
        """

        # Initialisation with SequenceMetric object
        seqmetric_obj = SequenceMetric.get_metric(mtype=sequence_metric)
        metric_obj = AggregationTrajectoryMetric(
            settings=AggregationTrajectoryMetricSettings(
                metric_mapper={
                    "pool_metrics": {
                        "event": seqmetric_obj,
                        "state": seqmetric_obj,
                        "interval": seqmetric_obj,
                    },
                }
            )
        )
        # Initialisation with string
        metric_str = AggregationTrajectoryMetric(
            settings=AggregationTrajectoryMetricSettings(
                metric_mapper={
                    "pool_metrics": {
                        "event": sequence_metric,
                        "state": sequence_metric,
                        "interval": sequence_metric,
                    }
                },
            )
        )

        # Collect results as dict
        dict_obj = metric_obj.collect_as_dict(trajectory_pool)
        dict_str = metric_str.collect_as_dict(trajectory_pool)
        dict_obj = replace_nan_with_value(dict_obj)
        dict_str = replace_nan_with_value(dict_str)
        sorted_dict_obj = dict(sorted(dict_obj.items()))
        sorted_dict_str = dict(sorted(dict_str.items()))

        # Check consistency
        assert sorted_dict_obj == sorted_dict_str
        # Verification via snapshot for both normalized results
        snapshot.assert_match(sorted_dict_obj)

    @pytest.mark.parametrize(
        "sequence_metric", ["linearpairwise", "softdtw", "lcs", "lcp", "edit", "dtw"]
    )
    def test_collect_as_matrix_equivalence_with_snapshot(
        self, trajectory_pool, sequence_metric, snapshot
    ):
        """
        Ensure collect_as_matrix gives the same result whether sequence metric is passed as object or string.
        Snapshot is used to check the actual content.
        """
        # Initialisation with SequenceMetric object
        seqmetric_obj = SequenceMetric.get_metric(mtype=sequence_metric)
        metric_obj = AggregationTrajectoryMetric(
            settings=AggregationTrajectoryMetricSettings(
                metric_mapper={
                    "pool_metrics": {
                        "event": seqmetric_obj,
                        "state": seqmetric_obj,
                        "interval": seqmetric_obj,
                    },
                }
            )
        )
        # Initialisation with string
        metric_str = AggregationTrajectoryMetric(
            settings=AggregationTrajectoryMetricSettings(
                metric_mapper={
                    "pool_metrics": {
                        "event": sequence_metric,
                        "state": sequence_metric,
                        "interval": sequence_metric,
                    }
                },
            )
        )

        # Collect results as matrix
        pd_matrix_obj = metric_obj.collect_as_matrix(trajectory_pool)
        pd_matrix_str = metric_str.collect_as_matrix(trajectory_pool)

        # Verification of equivalence
        assert pd_matrix_obj.equals(pd_matrix_str)
        # Verification via snapshot for both results
        snapshot.assert_match(pd_matrix_obj.to_csv())
