#!/usr/bin/env python3
"""
Trajectory class.
"""

import copy
import logging

from pypassist.mixin.cachable import Cachable
from pypassist.mixin.settings import SettingsMixin

from .settings.trajectory import TrajectorySettings
from ..sequence.base.exception import SequenceNotFoundError
from ..criterion.base.enum import CriterionLevel
from ..criterion.utils import resolve_and_init_criterion
from ..mixin.manipulation.trajectory import TrajectoryManipulationMixin
from ..mixin.summarizer.trajectory import TrajectorySummarizerMixin

LOGGER = logging.getLogger(__name__)


class Trajectory(
    Cachable,
    SettingsMixin,
    TrajectoryManipulationMixin,
    TrajectorySummarizerMixin,
):
    """
    A collection of sequences for a common ID value.
    """

    SETTINGS_DATACLASS = TrajectorySettings
    _IS_POOL = False  ## A flag to differentiate between TrajectoryPool and Trajectory

    def __init__(self, id_value, sequence_pools, static_data=None, settings=None):
        """
        Initialize a trajectory.

        Args:
            id_value: The common ID value for all sequences in this trajectory.
            sequence_pools: Dict mapping sequence names to SequencePool objects.
            static_data: Optional static data associated with this trajectory.
            settings: Optional settings for the trajectory.
        """
        self.id_value = id_value

        # Initialize with default settings if none provided
        if settings is None:
            settings = TrajectorySettings()

        SettingsMixin.__init__(self, settings)
        Cachable.__init__(self)
        TrajectoryManipulationMixin.__init__(self, static_data=static_data)

        self._sequence_pools = sequence_pools

    @Cachable.caching_property
    def sequences(self):
        """
        Dict mapping sequence names to Sequence objects for this ID.

        Returns:
            dict: Mapping from sequence names to Sequence objects.
        """
        sequences = {}
        for name, seq_pool in self._sequence_pools.items():
            try:
                sequences[name] = seq_pool[self.id_value]
                ## -- propagate T zero
                sequences[name]._t_zero = self.t_zero
            except SequenceNotFoundError:
                LOGGER.debug("Sequence %s not found for ID %s", name, self.id_value)
                continue
        return sequences

    def match(self, criterion, criterion_type=None, **kwargs):
        """
        Check if the trajectory matches a given criterion.

        Args:
            criterion (Union[Criterion, dict]):
                Defines the criterion, either as a dictionary or a Criterion
                object. Must be applicable at the trajectory level.
            criterion_type (str, optional):
                Indicates the type of criterion to apply, such as "static".
                Required if criterion is provided as a dictionary. Defaults to
                None.
            kwargs:
                Additional keyword arguments to override criterion attributes.

        Returns:
            bool: True if the trajectory matches the criterion, False otherwise.

        Examples:
            Test if trajectory belongs to elderly patient:

            >>> from tanat.criterion.mixin.static.settings import StaticCriterion
            >>> criterion = StaticCriterion(query="age > 60")
            >>> is_elderly = trajectory.match(criterion)
            >>> print(f"Is elderly patient: {is_elderly}")

            Test with custom criterion:

            >>> criterion = StaticCriterion(query="chronic_condition == True")
            >>> has_chronic = trajectory.match(criterion)
        """
        criterion, _ = resolve_and_init_criterion(
            criterion, "trajectory", criterion_type, CriterionLevel.TRAJECTORY
        )
        return bool(criterion.match(self, **kwargs))

    def filter(
        self, criterion, sequence_name, criterion_type=None, inplace=False, **kwargs
    ):
        """
        Filter entities in a specific sequence of the trajectory.

        Args:
            criterion (Union[Criterion, dict]):
                Defines the criterion, either as a dictionary or a Criterion
                object. The criterion must be applicable at the 'entity' level.
            sequence_name (str):
                The name of the sequence associated with the trajectory to
                apply the filter.
            criterion_type (str, optional):
                Indicates the type of criterion to apply, such as "query" or
                "pattern". Required if criterion is provided as a dictionary.
                Defaults to None.
            inplace (bool, optional):
                If True, modifies the current trajectory in place. Defaults to
                False.
            kwargs:
                Additional keyword arguments to override criterion attributes.

        Returns:
            Trajectory: A filtered trajectory or None if inplace.

        Examples:
            Filter entities without missing values in events sequence:

            >>> from tanat.criterion.mixin.query.settings import QueryCriterion
            >>> criterion = QueryCriterion(query="event_type.notna()")
            >>> clean_traj = trajectory.filter(criterion, "events")
            >>> print(f"Original: {len(trajectory['events'])}, "
            ...       f"Filtered: {len(clean_traj['events'])}")

            Filter emergency events only:

            >>> from tanat.criterion.mixin.pattern.settings import PatternCriterion
            >>> criterion = PatternCriterion(pattern={"event_type": "EMERGENCY"})
            >>> emergency_traj = trajectory.filter(criterion, "events")
        """
        # Direct delegation to sequence pool with single trajectory ID
        seqpool = self._sequence_pools[sequence_name]
        single_traj_seqpool = seqpool.subset([self.id_value])
        filtered_seqpool = single_traj_seqpool.filter(
            criterion, level="entity", criterion_type=criterion_type, **kwargs
        )

        if inplace:
            self._sequence_pools[sequence_name] = filtered_seqpool
            self.clear_cache()
            return None

        # Create new trajectory with filtered sequence pool
        return self._rebuild_with_filtered_sequence(sequence_name, filtered_seqpool)

    def _rebuild_with_filtered_sequence(self, sequence_name, filtered_seqpool):
        """
        Create a new trajectory with one sequence pool replaced by a filtered version.

        Args:
            sequence_name: Name of the sequence pool to replace.
            filtered_seqpool: The filtered sequence pool.

        Returns:
            Trajectory: New trajectory with the filtered sequence pool.
        """
        new_sequence_pools = {**self._sequence_pools}
        new_sequence_pools[sequence_name] = filtered_seqpool

        return Trajectory(
            self.id_value,
            new_sequence_pools,
            static_data=(
                self.static_data.copy() if self.static_data is not None else None
            ),
            settings=copy.deepcopy(self.settings),
        )

    def _get_sequence(self, name):
        """
        Internal method to get a specific sequence by name.

        Args:
            name: The name of the sequence to retrieve.

        Returns:
            Sequence: The requested sequence.

        Raises:
            SequenceNotFoundError: If no sequence with the given name exists.
        """
        try:
            return self.sequences[name]
        except KeyError as err:
            raise SequenceNotFoundError(
                f"No sequence named `{name}` for trajectory ID: {self.id_value}"
            ) from err

    def __getitem__(self, sequence_name):
        """
        Get a specific sequence by name.

        Args:
            sequence_name: The name of the sequence to retrieve.

        Returns:
            Sequence: The requested sequence.

        Raises:
            KeyError: If no sequence with the given name exists.
        """
        return self._get_sequence(sequence_name)

    def __len__(self):
        """
        Number of sequences in the trajectory
        """
        return len(self.sequences)

    def __repr__(self):
        """Return a string representation of the trajectory."""
        return self.summarize()
