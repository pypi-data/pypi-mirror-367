#!/usr/bin/env python3
"""
Base class for sequence criterion.
"""

from abc import abstractmethod

from ...base.applier import CriterionApplier
from .exception import (
    TrajectoryCriterionException,
    UnregisteredTrajectoryCriterionTypeError,
)


class TrajectoryCriterionApplier(CriterionApplier):
    """
    Base class for all sequence criterion.
    """

    _REGISTER = {}
    _TYPE_SUBMODULE = "../type"

    def match(self, trajectory, **kwargs):
        """
        Determine if a sequence matches this criterion.

        Args:
            sequence (Sequence): The sequence to evaluate.
            **kwargs: Additional keyword arguments to override criterion settings.

        Returns:
            bool: True if the sequence matches the criterion, False otherwise.
        """
        if not self._is_trajectory_instance(trajectory):
            raise TrajectoryCriterionException(
                f"Expected Trajectory, got {type(trajectory)}"
            )
        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            return self._match_impl(trajectory)

    @abstractmethod
    def _match_impl(self, trajectory):
        """
        Internal implementation of match method.
        """

    def filter(self, trajectory_pool, inplace=False, **kwargs):
        """
        Filter trajectories based on a given criterion.

        Args:
            trajectory_pool (TrajectoryPool): The trajectory pool to filter
            inplace (bool, optional): If True, modifies the current trajectory pool
                in place. Defaults to False.
            **kwargs: Additional keyword arguments to override criterion settings.

        Returns:
            TrajectoryPool: A new trajectory pool with trajectories that match the criterion.
        """
        if not self._is_trajectory_pool_instance(trajectory_pool):
            raise TrajectoryCriterionException(
                f"Expected TrajectoryPool, got {type(trajectory_pool)}"
            )
        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            return self._filter_impl(trajectory_pool, inplace)

    @abstractmethod
    def _filter_impl(self, trajectory_pool, inplace=False):
        """
        Internal implementation of filter trajectory method.
        """

    def which(self, trajectory_pool, **kwargs):
        """
        Get the IDs of sequences that satisfy this criterion.

        Args:
            trajectory_pool (SequencePool): The sequence pool to evaluate.
            **kwargs: Additional keyword arguments to override criterion settings.

        Returns:
            set: A set of sequence IDs that satisfy this criterion.
        """
        if not self._is_trajectory_pool_instance(trajectory_pool):
            raise TrajectoryCriterionException(
                f"Expected TrajectoryPool, got {type(trajectory_pool)}"
            )
        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            return self._which_impl(trajectory_pool)

    @abstractmethod
    def _which_impl(self, trajectory_pool):
        """
        Internal implementation of which method.
        """

    @classmethod
    def _unregistered_criterion_error(cls, criterion_type, err):
        """Raise an error for an unregistered trajectory criterion with a custom message."""
        registered = cls.list_registered()
        raise UnregisteredTrajectoryCriterionTypeError(
            f"Unknown trajectory criterion: '{criterion_type}'. "
            f"Available criterion: {registered}"
        ) from err
