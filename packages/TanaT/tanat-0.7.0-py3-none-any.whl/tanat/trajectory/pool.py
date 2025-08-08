#!/usr/bin/env python3
"""
Trajectory pool class.
"""

import logging
import itertools

from pypassist.mixin.cachable import Cachable
from pypassist.mixin.settings import SettingsMixin
from pypassist.utils.convert import ensure_list

from ..criterion.base.enum import CriterionLevel
from ..criterion.utils import resolve_and_init_criterion
from ..mixin.manipulation.trajectory import TrajectoryManipulationMixin
from ..mixin.summarizer.trajectory import TrajectorySummarizerMixin
from ..sequence.base.pool import SequencePool
from .exception import TrajectoryNotFoundError
from .trajectory import Trajectory
from .settings.pool import TrajectoryPoolSettings
from .settings.trajectory import TrajectorySettings

LOGGER = logging.getLogger(__name__)


class TrajectoryPool(
    Cachable,
    SettingsMixin,
    TrajectoryManipulationMixin,
    TrajectorySummarizerMixin,
):
    """
    The pool of trajectories.
    """

    SETTINGS_DATACLASS = TrajectoryPoolSettings
    _IS_POOL = True  ## A flag to differentiate between TrajectoryPool and Trajectory

    def __init__(self, sequence_pools, static_data=None, settings=None):
        """
        Initialize a trajectory pool.

        Args:
            sequence_pools: Dict mapping sequence names to SequencePool objects.
            static_data: Optional DataFrame of static data.
            settings: Optional settings for the trajectory pool.
            Required if static_data is provided.
        """
        self._sequence_pools = sequence_pools

        if settings is None:
            settings = TrajectoryPoolSettings()

        SettingsMixin.__init__(self, settings)
        Cachable.__init__(self)
        TrajectoryManipulationMixin.__init__(self, static_data=static_data)

    @Cachable.caching_property
    def sequence_pools(self):
        """
        Get a view of the sequence pools dictionary.

        Returns:
            dict: A view of the sequence pools dictionary.
        """
        sequence_pools = self._sequence_pools
        if self.settings.intersection:
            sequence_pools = {
                name: seqpool.subset(self.unique_ids, inplace=False)
                for name, seqpool in self._sequence_pools.items()
            }

        ## -- propagate T zero
        for seqpool in sequence_pools.values():
            seqpool._t_zero = self._t_zero
        return sequence_pools

    @Cachable.caching_property
    def unique_ids(self):
        """
        The set of unique IDs in the pool.
        """
        return self._derive_id_values(self._sequence_pools, self.settings.intersection)

    @Cachable.caching_property
    def trajectories(self):
        """
        Dict mapping ID values to Trajectory objects.

        Returns:
            dict: Mapping from ID values to Trajectory objects.
        """
        id_values = self.unique_ids
        seq_pools = self.sequence_pools
        static_data = self.static_data
        settings = TrajectorySettings(
            id_column=self.settings.id_column,
            static_features=self.settings.static_features,
        )

        trajectories = {}
        for id_val in id_values:
            trajectory = Trajectory(
                id_val,
                seq_pools,
                static_data=static_data,
                settings=settings,
            )
            # Use common t_zero propagation
            self._propagate_t_zero(trajectory, id_val)
            trajectories[id_val] = trajectory

        return trajectories

    @classmethod
    def init_from_seqpools(cls, static_data=None, settings=None, **seqpools_kwargs):
        """
        Initialize the trajectory pool from SequencePools in keyword arguments.

        Args:
            settings: Optional settings for the trajectory pool. If not provided,
                default settings will be used.
            static_data: Optional DataFrame containing feature data.
            **seqpools_kwargs: Dynamic keyword arguments where keys are sequence pool IDs
                and values are the corresponding sequence pool instances.

        Returns:
            TrajectoryPool: An instance of TrajectoryPool.

        Raises:
            ValueError: If no valid SequencePool is provided.
        """
        seqpools_kwargs, invalid_kwargs = cls._extract_seqpool_kwargs(seqpools_kwargs)
        cls._log_invalid_kwargs(invalid_kwargs)

        if not seqpools_kwargs:
            raise ValueError("No valid SequencePool provided.")
        return cls(
            sequence_pools=seqpools_kwargs,
            settings=settings,
            static_data=static_data,
        )

    @classmethod
    def init_empty(cls, static_data=None, settings=None):
        """
        Initialize a trajectory pool with no trajectories.

        Args:
            static_data: Optional DataFrame containing feature data.
            settings: Optional settings for the trajectory pool. If not provided,
                default settings will be used.

        Returns:
            TrajectoryPool: An empty trajectory pool with static data if provided.
        """
        return TrajectoryPool(
            sequence_pools={}, static_data=static_data, settings=settings
        )

    def add_sequence_pool(self, sequence_pool, sequence_name, override=False):
        """
        Add a sequence pool to the trajectory pool.

        Args:
            sequence_pool: The sequence pool to add.
            sequence_name: The name of the sequence pool.
            override: If True, overwrites the existing sequence pool with the same
                name. Defaults to False.

        Returns:
            self: for method chaining
        """
        if sequence_name in self._sequence_pools and not override:
            raise ValueError(
                f"Sequence pool with name '{sequence_name}' already exists."
                " Use override=True to overwrite it."
            )

        if not isinstance(sequence_pool, SequencePool):
            raise ValueError(
                "sequence_pool must be an instance of SequencePool. "
                f"Got: {sequence_pool!r}"
            )

        self._sequence_pools[sequence_name] = sequence_pool
        self.clear_cache()
        return self

    def iter_pairs(self):
        """
        Get all pairs of trajectories in the trajectory pool.

        Returns:
            iterator: An iterator yielding pairs of Trajectory objects.
        """
        # pylint: disable=not-an-iterable
        trajectories = [self[id_val] for id_val in self.unique_ids]
        return itertools.product(trajectories, repeat=2)

    def filter(
        self,
        criterion,
        level=None,
        sequence_name=None,
        inplace=False,
        intersection=None,
        criterion_type=None,
        **kwargs,
    ):
        """
        Filter trajectories, sequences or entities based on a given criterion.

        Args:
            criterion (Union[Criterion, dict]):
                Defines the criterion, either as a dictionary or a Criterion
                object.
            level (str, optional):
                Specifies the level to apply the criterion, either "trajectory",
                "sequence" or "entity". Required if criterion is applicable at
                multiple levels or if criterion is a dictionary. Defaults to None.
            sequence_name (str):
                The name of the sequence associated with the trajectory to
                evaluate. Required if criterion will be applied at "entity" or
                "sequence" level.
            inplace (bool, optional):
                If set to True, modifies the current trajectory pool in place.
                Defaults to False.
            intersection (bool, optional):
                Whether to use intersection mode for trajectory IDs.
                Defaults to None.
            criterion_type (str, optional):
                Indicates the type of criterion to apply, such as "query" or
                "pattern". Required if criterion is provided as a dictionary.
                Defaults to None.
            kwargs:
                Additional keyword arguments to override criterion attributes.

        Returns:
            TrajectoryPool:
                Returns a new filtered trajectory pool, or None if inplace is
                True.

        Examples:
            Filter by static data (trajectory level):

            >>> from tanat.criterion.mixin.static.settings import StaticCriterion
            >>> criterion = StaticCriterion(query="age > 50")
            >>> elderly_pool = traj_pool.filter(criterion, level="trajectory")

            Filter by sequence events:

            >>> from tanat.criterion.mixin.pattern.settings import PatternCriterion
            >>> criterion = PatternCriterion(pattern={"event_type": "EMERGENCY"})
            >>> emergency_pool = traj_pool.filter(
            ...     criterion, level="sequence", sequence_name="events"
            ... )

            Filter entities in a specific sequence:

            >>> from tanat.criterion.mixin.query.settings import QueryCriterion
            >>> criterion = QueryCriterion(query="event_type.notna()")
            >>> clean_pool = traj_pool.filter(
            ...     criterion, level="entity", sequence_name="events"
            ... )
        """
        # -- validate, resolve, and initialize criterion
        criterion_applier, resolved_level = resolve_and_init_criterion(
            criterion, level, criterion_type, CriterionLevel.TRAJECTORY
        )

        # Validate sequence_name for non-trajectory levels
        if resolved_level != CriterionLevel.TRAJECTORY and sequence_name is None:
            raise ValueError(
                "sequence_name must be provided for 'entity' or 'sequence' level."
            )

        # -- Trajectory level
        if resolved_level == CriterionLevel.TRAJECTORY:
            return self._apply_trajectory_filter(
                criterion_applier, inplace, intersection, **kwargs
            )

        ## -- Delegate to sequence pool
        return self._filter_from_sequence_pool(
            criterion_applier.settings,
            resolved_level,
            sequence_name,
            inplace,
            intersection,
            **kwargs,
        )

    def subset(self, id_values, inplace=False):
        """
        Subset the trajectory pool to include only the specified ID values.

        Args:
            id_values: List of ID values to include in the subset.
            inplace: If True, modify the trajectory pool in place. Default is
                False.

        Returns:
            TrajectoryPool: A new trajectory pool with the specified ID values
                (or self if inplace=True).

        Examples:
            Create subset from specific trajectory IDs:

            >>> subset_pool = traj_pool.subset(["seq-1", "seq-3", "seq-5"])
            >>> print(f"Subset contains {len(subset_pool)} trajectories")

            Multi-step analysis workflow:

            >>> # Step 1: Find elderly patients
            >>> from tanat.criterion.mixin.static.settings import StaticCriterion
            >>> elderly_criterion = StaticCriterion(query="age > 60")
            >>> elderly_ids = traj_pool.which(elderly_criterion)
            >>> # Step 2: Create subset for further analysis
            >>> elderly_subset = traj_pool.subset(elderly_ids)
        """
        id_values = ensure_list(id_values)
        dict_seqpool = {}
        for seqpool_id, seqpool in self.sequence_pools.items():
            seqpool = seqpool.subset(id_values)
            dict_seqpool[seqpool_id] = seqpool

        static_data = self._subset_static_data(id_values)

        if inplace:
            self._sequence_pools = dict_seqpool
            self._static_data = static_data
            self.clear_cache()
            return None

        copy_settings = self.settings.__class__(**self.settings.__dict__)
        return TrajectoryPool(
            sequence_pools=dict_seqpool,
            settings=copy_settings,
            static_data=static_data,
        )

    def which(self, criterion, criterion_type=None, **kwargs):
        """
        Get the IDs of trajectories that match the criterion.

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
            set: A set of trajectory IDs that match the criterion.

        Examples:
            Find elderly patients:

            >>> from tanat.criterion.mixin.static.settings import StaticCriterion
            >>> criterion = StaticCriterion(query="age > 60")
            >>> elderly_ids = traj_pool.which(criterion)
            >>> print(f"Found {len(elderly_ids)} elderly patients")

            Use with subset for two-step filtering:

            >>> elderly_subset = traj_pool.subset(elderly_ids)
        """
        # -- validate, resolve, and initialize criterion
        traj_criterion, _ = resolve_and_init_criterion(
            criterion, "trajectory", criterion_type, CriterionLevel.TRAJECTORY
        )

        return traj_criterion.which(self, **kwargs)

    def __getitem__(self, id_val):
        """
        Get the trajectory for a specific ID value.

        Args:
            id_val: The ID value to retrieve the trajectory for.

        Returns:
            Trajectory: The trajectory for the specified ID value.

        Raises:
            KeyError: If the ID value is not in this trajectory pool.
        """
        # pylint: disable=unsupported-membership-test
        if id_val not in self.unique_ids:
            raise TrajectoryNotFoundError(
                f"ID value {id_val} not found in this trajectory pool."
            )
        return self.trajectories[id_val]

    def __len__(self):
        """
        Number of trajectories in the pool
        """
        return len(self.unique_ids)

    @classmethod
    def _log_invalid_kwargs(cls, invalid_pool):
        """
        Log warnings for invalid SequencePool keyword arguments.

        Args:
            invalid_pool: List of invalid keyword argument strings that were
                expected to be valid SequencePool instances.
        """
        if invalid_pool:
            LOGGER.warning(
                "Ignoring invalid SequencePool(s): %s",
                ", ".join(invalid_pool),
            )

    @classmethod
    def _extract_seqpool_kwargs(cls, seqpools_kwargs):
        """
        Extract valid sequence pools from seqpools_kwargs.

        Args:
            seqpools_kwargs: Dict of sequence pool arguments.

        Returns:
            tuple: (valid_pools, invalid_pool) where valid_pools is a dict of
                valid sequence pools and invalid_pool is a list of invalid
                keyword argument strings.
        """
        valid_pools = {}
        invalid_pool = []
        for seqpool_id, seqpool in seqpools_kwargs.items():
            if isinstance(seqpool, SequencePool):
                valid_pools[seqpool_id] = seqpool
            else:
                invalid_pool.append(f"{seqpool_id}: {seqpool!r}")
        return valid_pools, invalid_pool

    @staticmethod
    def _derive_id_values(sequence_pools, intersection):
        """
        Derive the id_values based on the sequence pools.

        Args:
            sequence_pools: Dict of sequence pools.
            intersection: Whether to take the intersection or union of ID values.

        Returns:
            set: The derived set of ID values.
        """
        id_values = None
        for seq_pool in sequence_pools.values():
            new_values = set(seq_pool.unique_ids)
            if id_values is None:
                id_values = new_values
            elif intersection:
                id_values.intersection_update(new_values)
            else:
                id_values.update(new_values)
        return id_values if id_values else set()

    def _apply_trajectory_filter(
        self, criterion_applier, inplace, intersection, **kwargs
    ):
        """
        Handle filtering at trajectory level.
        """
        result = criterion_applier.filter(self, inplace, **kwargs)

        if intersection is not None:
            if inplace:
                self.update_settings(intersection=intersection)
            else:
                result.update_settings(intersection=intersection)

        return result if not inplace else None

    def _filter_from_sequence_pool(
        self, criterion, resolved_level, sequence_name, inplace, intersection, **kwargs
    ):
        """
        Handle filtering at sequence or entity level by delegating to sequence pool.
        """
        # Get the target sequence pool
        seqpool = self.sequence_pools.get(sequence_name)
        if seqpool is None:
            raise ValueError(f"Sequence pool with name '{sequence_name}' not found.")

        # Apply filter to the sequence pool
        seqpool_filtered = seqpool.filter(criterion, resolved_level, False, **kwargs)

        if inplace:
            # Modify current trajectory pool in place
            self._sequence_pools[sequence_name] = seqpool_filtered
            self.clear_cache()
            if intersection is not None:
                self.update_settings(intersection=intersection)
            return None

        # Create new trajectory pool with filtered sequence pool
        new_traj_pool = TrajectoryPool.init_empty(
            settings=self.settings.__class__(**self.settings.__dict__),
            static_data=(
                self.static_data.copy() if self.static_data is not None else None
            ),
        )

        if intersection is not None:
            new_traj_pool.update_settings(intersection=intersection)

        # Add all sequence pools (filtered one and unchanged ones)
        for seqpool_id, seqpool in self.sequence_pools.items():
            if seqpool_id == sequence_name:
                new_traj_pool.add_sequence_pool(seqpool_filtered, seqpool_id)
            else:
                new_traj_pool.add_sequence_pool(seqpool, seqpool_id)

        return new_traj_pool

    def __repr__(self):
        """Return a string representation of the trajectory pool."""
        return self.summarize()
