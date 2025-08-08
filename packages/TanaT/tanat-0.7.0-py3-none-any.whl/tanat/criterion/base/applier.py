#!/usr/bin/env python3
"""
Base class for criterion applier.
"""

from abc import ABC, abstractmethod

from pypassist.mixin.registrable import Registrable, UnregisteredTypeError
from pypassist.mixin.settings import SettingsMixin
from pydantic_core import core_schema

from .settings import Criterion
from ...sequence.base.sequence import Sequence
from ...sequence.base.pool import SequencePool
from ...trajectory.pool import TrajectoryPool
from ...trajectory.trajectory import Trajectory


class CriterionApplier(ABC, Registrable, SettingsMixin):
    """
    Abstract base class for all criterion appliers in the TanaT framework.

    Provides a standardized interface for initializing and managing
    criterion-based filtering across different data types and levels.
    """

    def __init__(self, settings):
        """
        Initialize the CriterionApplier with specific settings.

        Args:
            settings: Criterion object defining filtering parameters.
        """
        SettingsMixin.__init__(self, settings)

    @classmethod
    def init(cls, criterion, criterion_type=None):
        """
        Initialize a Criterion applier class dynamically.

        Supports initialization from dictionary or Criterion object.

        Args:
            criterion: Criterion settings (dict or Criterion object)
            criterion_type: Type of criterion for registry resolution

        Returns:
            Configured Criterion applier instance

        Raises:
            ValueError: If initialization parameters are invalid
        """
        if isinstance(criterion, dict):
            if criterion_type is None:
                raise ValueError(
                    "criterion_type must be provided if settings is a dictionary."
                )

        else:
            if not isinstance(criterion, Criterion):
                raise ValueError(
                    f"settings must be a Criterion object or a dictionary. "
                    f"Got {criterion!r}."
                )
            # pylint: disable=protected-access
            criterion_type = criterion._REGISTER_NAME

        try:
            criterion = cls.get_registered(criterion_type)(settings=criterion)
        except UnregisteredTypeError as err:
            cls._unregistered_criterion_error(criterion_type, err)

        return criterion

    def _is_sequence_instance(self, sequence):
        """
        Check if the given object is a Sequence instance.

        Args:
            sequence: Object to check

        Returns:
            bool: True if object is a Sequence, False otherwise
        """
        return isinstance(sequence, Sequence)

    def _is_sequence_pool_instance(self, sequence_pool):
        """
        Check if the given object is a SequencePool instance.

        Args:
            sequence_pool: Object to check

        Returns:
            bool: True if object is a SequencePool, False otherwise
        """
        return isinstance(sequence_pool, SequencePool)

    def _is_trajectory_pool_instance(self, trajectory_pool):
        """
        Check if the given object is a TrajectoryPool instance.

        Args:
            trajectory_pool: Object to check

        Returns:
            bool: True if object is a TrajectoryPool, False otherwise
        """
        return isinstance(trajectory_pool, TrajectoryPool)

    def _is_trajectory_instance(self, trajectory):
        """
        Check if the given object is a Trajectory instance.

        Args:
            trajectory: Object to check

        Returns:
            bool: True if object is a Trajectory, False otherwise
        """
        return isinstance(trajectory, Trajectory)

    @classmethod
    @abstractmethod
    def _unregistered_criterion_error(cls, criterion_type, err):
        """
        Raise a custom error for unregistered criterion types.

        Args:
            criterion_type: Type of unregistered criterion
            err: Original UnregisteredTypeError

        Raises:
            Custom exception specific to the criterion context
        """

    def __get_pydantic_core_schema__(self, handler):  # pylint: disable=unused-argument
        """
        Provide a custom Pydantic core schema for validation.

        Returns:
            Pydantic core schema for this class
        """
        return core_schema.any_schema()
