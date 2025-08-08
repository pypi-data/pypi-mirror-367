#!/usr/bin/env python3
"""
Zero setter base class.
"""

from abc import ABC, abstractmethod
import logging

from pypassist.mixin.settings import SettingsMixin
from pypassist.mixin.registrable import Registrable, UnregisteredTypeError

from .exception import UnregisteredZeroSetterTypeError

LOGGER = logging.getLogger(__name__)


class ZeroSetter(ABC, Registrable, SettingsMixin):
    """
    Base class for zero setters.
    Handles both sequence and trajectory objects (single or pool).
    """

    _TYPE_SUBMODULE = "type"
    _REGISTER = {}

    def __init__(self, settings):
        SettingsMixin.__init__(self, settings)
        self._data_dict = None  # Placeholder for data dictionary if needed

    @abstractmethod
    def assign(self, target, **kwargs):
        """
        Assign T0 to a sequence, trajectory, or their pools.

        Args:
            target: Single sequence/trajectory or pool object
            **kwargs: Additional keyword arguments to override settings
        """

    @classmethod
    def init(cls, settings, zero_setter_type=None):
        """
        Initialize the zero setter.

        Args:
            settings: Settings for the zero setter
            zero_setter_type: Type of the zero setter

        Returns:
            An instance of the zero setter
        """
        if isinstance(settings, dict):
            if zero_setter_type is None:
                raise ValueError(
                    "zero_setter_type must be provided if settings is a dictionary."
                )

        if zero_setter_type is None:
            zero_setter_type = getattr(settings, "_REGISTER_NAME", None)

        if zero_setter_type is None:
            raise ValueError(
                "Settings seems not to be a valid dataclass type "
                "(missing _REGISTER_NAME)."
            )

        try:
            zero_setter = cls.get_registered(zero_setter_type)(settings=settings)
        except UnregisteredTypeError as err:
            raise UnregisteredZeroSetterTypeError(
                f"Unknown zero setter type: '{zero_setter_type}'. "
                f"Available zero setter types: {cls.list_registered()}"
            ) from err

        return zero_setter

    def _detect_target_type(self, target):
        """
        Detect the type of target object.

        Args:
            target: Object to analyze

        Returns:
            Tuple (container_type, is_pool) where:
            - container_type: 'sequence' or 'trajectory'
            - is_pool: True if it's a pool, False if single object
        """
        container_type = getattr(target, "_container_type", None)
        if container_type is None:
            raise ValueError(
                "Zeroing: Input object should be either a sequence, "
                "SequencePool, a trajectory or a TrajectoryPool. "
                f"Got: {target!r}"
            )
        is_pool = target._is_pool  # pylint: disable=protected-access
        return container_type, is_pool

    def _get_target_ids(self, target):
        """
        Extract target IDs from sequence/trajectory or pool object.

        Args:
            target: Target object (sequence, trajectory, or pool)

        Returns:
            List or single ID value
        """
        if hasattr(target, "unique_ids"):
            return target.unique_ids
        return target.id_value

    def _clear_cache_and_return(self, target):
        """
        Clear transform cache (if exists) and return target.

        Args:
            target: Target object

        Returns:
            The same target object
        """
        if hasattr(target, "_transformer"):
            # pylint: disable=protected-access
            target._transformer.clear_cache()
        return target

    def _set_with_anchor_resolution(self, target, **kwargs):
        """
        Common logic for setting t_zero with anchor resolution.

        Args:
            target: The target object (sequence, pool, or trajectory).
            **kwargs: Additional keyword arguments to override settings.

        Returns:
            The target object with t_zero set.
        """
        if self.settings.anchor is None:  # If anchor is not provided
            anchor = self._resolve_anchor(target)
            if "anchor" not in kwargs:
                # Only add anchor if not already provided
                kwargs["anchor"] = anchor

        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            object_type, _ = self._detect_target_type(target)
            # pylint: disable=no-member
            if object_type == "sequence":
                t_zero = self._handle_sequence(target)  # implemented in subclasses
            else:  # trajectory
                t_zero = self._handle_trajectory(target)
            target._t_zero = t_zero
            return self._clear_cache_and_return(target)

    def _build_data_dict(self, trajectory_or_pool):
        """Build standardized data dictionary from trajectory or pool."""
        if self._data_dict is not None:
            return self._data_dict

        is_pool = hasattr(trajectory_or_pool, "unique_ids")
        data_dict = {}

        for seq_name, seq_pool in trajectory_or_pool._sequence_pools.items():
            seq_data = self._extract_sequence_data(
                seq_pool, trajectory_or_pool, is_pool
            )
            if seq_data is not None:
                data_dict[seq_name] = {
                    "settings": seq_pool.settings,
                    "data": seq_data,
                }
        self._data_dict = data_dict
        return data_dict

    def _extract_sequence_data(self, seq_pool, trajectory_or_pool, is_pool):
        """Extract data from a sequence pool."""
        seq_data = seq_pool._get_standardized_data()

        if not is_pool:
            try:
                seq_data = seq_data.loc[trajectory_or_pool.id_value]
            except KeyError:
                LOGGER.debug(
                    "%s: Trajectory %s not found in pool %s. Skipping",
                    self.__class__.__name__.capitalize(),
                    trajectory_or_pool.id_value,
                    seq_pool,
                )
                return None

        return seq_data

    def _validate_sequence_name_in_data_dict(self, data_dict):
        """
        Validate that the sequence exists in the data dictionary.

        Args:
            data_dict: Data dictionary containing sequences

        Raises:
            ValueError: If the sequence is not found
        """
        if self.settings.sequence_name not in data_dict:
            raise ValueError(
                f"Sequence '{self.settings.sequence_name}' not found. "
                f"Available sequences: {list(data_dict.keys())}"
            )

    def _resolve_anchor(self, target):
        """
        Resolve anchor parameter based on target type.

        Args:
            target: Target object (sequence or trajectory)

        Returns:
            str: Resolved anchor value
        """
        # pylint: disable=protected-access
        object_type, _ = self._detect_target_type(target)
        if object_type == "sequence":
            return target._resolve_anchor()
        # Trajectory case
        data_dict = self._build_data_dict(target)
        self._validate_sequence_name_in_data_dict(data_dict)

        # we can assume that the sequence name is valid from target._sequence_pools
        return target._sequence_pools[self.settings.sequence_name]._resolve_anchor()
