#!/usr/bin/env python3
"""
Base class for registable Trajectory metrics.
"""

from abc import abstractmethod
import logging

import numpy as np
import pandas as pd

# from pypassist.utils.export import export_to_csv
from pypassist.mixin.cachable import Cachable
from pypassist.runner.workenv.mixin.processor import ProcessorMixin

from .exception import UnregisteredTrajectoryMetricTypeError
from ...base import Metric
from ....trajectory.pool import TrajectoryPool
from ....trajectory.trajectory import Trajectory

LOGGER = logging.getLogger(__name__)


class TrajectoryMetric(Metric, ProcessorMixin):
    """
    Base class for trajectory metrics that compares pairs of trajectories
    within a trajectory pool.
    """

    _REGISTER = {}

    def __init__(self, settings, *, workenv=None):
        """
        Args:
            settings:
                The metric settings.

            workenv:
                Optional workenv instance.
        """
        Metric.__init__(self, settings, workenv=workenv)
        ProcessorMixin.__init__(self)

    @abstractmethod
    def __call__(self, traj_a, traj_b, **kwargs):
        """
        Compare two trajectories.

        Args:
            traj_a (Trajectory):
                First trajectory to compare.
            traj_b (Trajectory):
                Second trajectory to compare.
            kwargs:
                Optional arguments to override specific settings.

        Returns:
            float: The metric value for the sequence pair.
        """

    @Cachable.caching_method()
    def collect_as_dict(self, trajectory_pool, **kwargs):
        """
        Compute and collect the metric for all pairs of trajectories in the trajectory pool.

        Args:
            trajectory_pool (TrajectoryPool):
                The trajectory pool containing trajectories.
            kwargs:
                Optional arguments to override specific settings.

        Returns:
            dict: Metric results for each pair of trajectories.
        """
        return dict(self.collect(trajectory_pool, **kwargs))

    def collect(self, trajectory_pool, **kwargs):
        """
        Lazily compute and collect the metric for all pairs of trajectories
        in the trajectory pool.

        Args:
            trajectory_pool (TrajectoryPool):
                The trajectory pool containing trajectories.
            kwargs:
                Optional arguments to override specific settings.

        Yields:
            tuple: Pair IDs and their computed metric.
        """
        self._validate_trajectory_pool(trajectory_pool)
        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            for pair in trajectory_pool.iter_pairs():
                traj_a, traj_b, pair_ids = self._extract_elts_and_ids(pair)
                yield pair_ids, self(traj_a, traj_b)

    def collect_as_matrix(
        self,
        trajectory_pool,
        *,
        missing_value=np.nan,
        sparse=False,
        **kwargs,
    ):
        """
        Generate a collection matrix from the metric results using lazy evaluation.

        Args:
            trajectory_pool (TrajectoryPool):
                Pool of trajectories to collect metrics from.
            missing_value (float):
                The value to use for missing values in the matrix.
            sparse (bool):
                If True, return a sparse matrix without filling the lower part and missing values.
            kwargs (Optional[Any]):
                Additional settings that override the default configuration.

        Returns:
            pd.DataFrame: DataFrame containing the matrix of metric results
            for the trajectory pairs.
        """
        collection = self.collect_as_dict(trajectory_pool, **kwargs)

        df_pairs = pd.DataFrame(collection.items(), columns=["pair", "value"])
        df_pairs[["id_a", "id_b"]] = df_pairs["pair"].tolist()

        matrix_df = df_pairs.pivot(index="id_a", columns="id_b", values="value")
        matrix_df.index.name = None

        if not sparse:
            matrix_df = matrix_df.combine_first(matrix_df.T)
            matrix_df.fillna(float(missing_value), inplace=True)

        return matrix_df

    def _validate_trajectory_pool(self, trajectory_pool):
        """
        Validate trajectory pool
        """
        if not isinstance(trajectory_pool, TrajectoryPool):
            raise ValueError(
                f"Invalid trajectory pool. Expected TrajectoryPool, got {type(trajectory_pool)}."
            )

    def _validate_trajectories(self, **trajectories):
        """
        Validate multiple trajectories, ensuring they are of the correct type.

        Args:
            trajectories:
                Dictionary of trajectories to validate.

        Raises:
            ValueError: If any trajectory is invalid.
        """
        for key, trajectory in trajectories.items():
            if not self._is_valid_trajectory(trajectory):
                raise ValueError(
                    f"Invalid trajectory '{key}'. Expected Trajectory, got {type(trajectory)}."
                )

    def _is_valid_trajectory(self, trajectory):
        """
        Check if a given trajectory is valid.

        Args:
            trajectory:
                The trajectory to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        return isinstance(trajectory, Trajectory)

    @classmethod
    def _unregistered_metric_error(cls, mtype, err):
        """Raise an error for an unregistered trajectory metric with a custom message."""
        registered = cls.list_registered()
        raise UnregisteredTrajectoryMetricTypeError(
            f"Unknown trajectory metric: '{mtype}'. " f"Available metrics: {registered}"
        ) from err
