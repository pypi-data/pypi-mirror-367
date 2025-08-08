#!/usr/bin/env python3
"""
Manipulation mixin for Sequence and SequencePool objects.
"""

import copy

from .base import BaseManipulationMixin
from .data.sequence import SequenceDataMixin
from .data.static import StaticDataMixin
from ...time.anchor import DateAnchor


class SequenceManipulationMixin(
    BaseManipulationMixin, SequenceDataMixin, StaticDataMixin
):
    """
    Mixin providing manipulation methods for Sequence and SequencePool objects.
    Includes sequence data access, static data access, and manipulation capabilities.
    """

    # -- flag to distiguish between Trajectory/TrajectoryPool and Sequence/SequencePool
    ## -- usefull to control type when isinstance triggers a circular import
    _CONTAINER_TYPE = "sequence"

    def __init__(self, sequence_data, static_data=None, metadata=None):
        BaseManipulationMixin.__init__(self)
        SequenceDataMixin.__init__(self, sequence_data, metadata)
        StaticDataMixin.__init__(self, static_data)

    def _get_copy_data(self, deep):
        """
        Extract data for copy operation based on sequence.

        Args:
            deep (bool): If True, create a deep copy. Default True.

        Returns:
            tuple: The extracted data to copy.
        """
        return (
            self._copy_sequence_data(deep),
            self._copy_settings(deep),
            self._copy_metadata(deep),
            self._copy_static_data(deep),
        )

    def _copy_sequence_data(self, deep):
        """Create a copy of sequence data."""
        return self.sequence_data.copy(deep=deep)

    def _copy_settings(self, deep):
        """Create a copy of dataclass settings."""
        if deep:
            return copy.deepcopy(self.settings)
        return copy.copy(self.settings)

    def _copy_metadata(self, deep):
        """Create a copy of metadata if it exists."""
        if self.metadata is None:
            return None
        if deep:
            return copy.deepcopy(self.metadata)
        return copy.copy(self.metadata)

    def _copy_static_data(self, deep):
        """Create a copy of static data if it exists."""
        if self.static_data is None:
            return None
        return self.static_data.copy(deep=deep)

    def _create_copy_instance(self, copy_data):
        """
        Create new sequence instance with copied data.

        Args:
            copy_data (tuple): Data to copy into the new instance.

        Returns:
            Sequence or SequencePool: New instance with copied data.
        """
        sequence_data, settings, metadata, static_data = copy_data
        # pylint: disable=E1121
        if self._is_pool:
            # SequencePool case
            new_instance = self.__class__(
                sequence_data, settings, metadata, static_data
            )
        else:
            # Single sequence case
            new_instance = self.__class__(
                self.id_value,
                sequence_data,
                settings,
                metadata,
                static_data,
            )

        self._propagate_t_zero(new_instance)
        return new_instance

    def _resolve_anchor(self, anchor=None):
        """
        Resolve anchor parameter with clear type-based logic.

        Args:
            anchor (str, optional): User-provided anchor value

        Returns:
            str: Resolved anchor value
        """
        if anchor is not None:
            # return validated anchor
            return DateAnchor.from_str(anchor)

        sequence_type = self.get_registration_name()

        if sequence_type == "interval":
            # For intervals, use settings anchor
            return DateAnchor.from_str(self.settings.anchor)
        # For events and states, anchor is always 'start'
        return DateAnchor.START

    ## ----- ZEROING ----- ##

    def zero_from_position(self, position=0, anchor=None):
        """
        Set t_zero based on entity position in the sequence.

        Args:
            position (int): Position of the entity (0-based)
            anchor (DateAnchor, optional): Reference point within periods for time calculation.
                Auto-resolved by sequence type if not specified:
                - EventSequence: 'start' (events are points in time)
                - StateSequence: 'start' (beginning of state periods)
                - IntervalSequence: uses sequence settings anchor
                Override with explicit anchor for custom resolution strategy.

        Returns:
            self: For method chaining

        Examples:
            >>> # For any sequence type
            >>> seqpool.zero_from_position(1)

            >>> # For intervals with specific anchor
            >>> interval_pool.zero_from_position(1, anchor="middle")
        """
        settings_dict = {"position": position, "anchor": anchor}
        indexer = self._zeroing_base_class.init(
            settings=settings_dict, zero_setter_type="position"
        )
        indexer.assign(self)
        return self

    def zero_from_query(self, query, use_first=True, anchor=None):
        """
        Set t_zero based on a query over sequence data.

        Args:
            query (str): Query string to filter sequence data
            use_first (bool): If True, use first matching row; if False, use last matching row
            anchor (DateAnchor, optional): Reference point within periods for time calculation.
                Auto-resolved by sequence type if not specified:
                - EventSequence: 'start' (events are points in time)
                - StateSequence: 'start' (beginning of state periods)
                - IntervalSequence: uses sequence settings anchor
                Override with explicit anchor for custom resolution strategy.

        Returns:
            self: For method chaining

        Examples:
            >>> # Query with auto-resolved anchor
            >>> seqpool.zero_from_query("feature == 'A'")

            >>> # Query with explicit anchor for intervals
            >>> interval_pool.zero_from_query("feature == 'B'", anchor="middle")

            >>> # Query with explicit anchor for states
            >>> state_pool.zero_from_query("feature == 'C'", anchor="end")
        """
        settings_dict = {"query": query, "use_first": use_first, "anchor": anchor}
        indexer = self._zeroing_base_class.init(
            settings=settings_dict, zero_setter_type="query"
        )
        indexer.assign(self)
        return self

    @property
    def vocabulary(self):
        """
        Return the vocabulary of sequence data.
        """
        features = self.settings.entity_features
        data_rows = self.sequence_data[features].values

        if len(features) > 1:
            # -- muliple features, tuple
            return set(tuple(item) for item in data_rows)

        return set(data_rows.flatten())

    def clear_cache(self):
        """
        Clear all cached data and reset the transformer.
        """
        super().clear_cache()
        self._reset_transformer()
