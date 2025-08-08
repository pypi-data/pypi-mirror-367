#!/usr/bin/env python3
"""
Aggregation trajectory metric for testing.
"""

import logging
from collections import defaultdict

from .settings import AggregationTrajectoryMetricSettings
from ...base.metric import TrajectoryMetric
from ...settings.mapper import MetricMapper

LOGGER = logging.getLogger(__name__)


class AggregationTrajectoryMetric(TrajectoryMetric, register_name="aggregation"):
    """
    Computes an aggregated metric value between two trajectories.
    """

    SETTINGS_DATACLASS = AggregationTrajectoryMetricSettings

    def __init__(self, settings=None, *, workenv=None):
        if settings is None:
            settings = AggregationTrajectoryMetricSettings()
        super().__init__(settings=settings, workenv=workenv)

    @property
    def agg_fun(self):
        """Returns the aggregation function."""
        agg_fun = self._settings.agg_fun
        if isinstance(agg_fun, str):
            return self._resolve_agg_fun(agg_fun)
        if callable(agg_fun):
            return agg_fun
        raise ValueError(
            "Aggregation function must be callable or a valid string identifier."
        )

    def __call__(self, traj_a, traj_b, **kwargs):
        """Compare two trajectories."""
        self._validate_trajectories(traj_a=traj_a, traj_b=traj_b)

        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            seq_names = set(traj_a.sequences.keys()).union(traj_b.sequences.keys())
            metrics = self._get_metrics_for_sequences(seq_names)
            values = []

            for seq_name, metric in metrics.items():
                seq_a = traj_a.sequences.get(seq_name)
                seq_b = traj_b.sequences.get(seq_name)
                if seq_a and seq_b:
                    values.append(metric(seq_a, seq_b))

            if not self._has_sufficient_results(values, len(metrics)):
                return self._settings.default_value

            # pylint: disable=not-callable
            return self.agg_fun(values) if values else self._settings.default_value

    def collect_as_dict(self, trajectory_pool, **kwargs):
        """Compute metrics for all trajectory pairs in the pool."""
        self._validate_trajectory_pool(trajectory_pool)
        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            metrics = self._get_metrics_for_sequences(
                trajectory_pool.sequence_pools.keys()
            )
            return self._process_results(
                self._collect_sequence_metrics(trajectory_pool, metrics)
            )

    def _get_metrics_for_sequences(self, seq_names):
        """Get metrics for sequence names, creating default mapper if needed."""
        if self._settings.metric_mapper is None:
            self._settings.metric_mapper = MetricMapper()
        return {
            name: self._settings.metric_mapper.get_metric_for_pool(name)
            for name in seq_names
        }

    def _collect_sequence_metrics(self, trajectory_pool, metrics):
        """Collect metrics for all sequences in the pool."""
        results = defaultdict(list)
        for seq_name, metric in metrics.items():
            seq_pool = trajectory_pool.sequence_pools.get(seq_name)
            if not seq_pool:
                LOGGER.warning("Missing sequence pool: %s", seq_name)
                continue

            seq_results = metric.collect_as_dict(seq_pool)
            for pair_id, value in seq_results.items():
                results[pair_id].append(value)
        return results

    def _has_sufficient_results(self, values, expected_count):
        """Check if we have enough results based on intersection setting."""
        if self._settings.intersection and len(values) < expected_count:
            LOGGER.warning(
                "Insufficient results, expected %d got %d", expected_count, len(values)
            )
            return False
        return True

    def _process_results(self, results):
        """Process and aggregate results."""
        if not results:
            return {}

        min_results = len(next(iter(results.values())))
        processed = {}
        for pair_id, values in results.items():
            if self._settings.intersection and len(values) < min_results:
                continue
            processed[pair_id] = self.agg_fun(values)  # pylint: disable=not-callable
        return processed
