#!/usr/bin/env python3
"""
Manipulation mixin for Trajectory and TrajectoryPool objects.
"""

from .base import BaseManipulationMixin
from .data.static import StaticDataMixin


class TrajectoryManipulationMixin(BaseManipulationMixin, StaticDataMixin):
    """
    Mixin providing manipulation methods for Trajectory and TrajectoryPool objects.
    Includes static data access and manipulation capabilities.
    """

    # -- flag to distiguish between Trajectory/TrajectoryPool and Sequence/SequencePool
    ## -- usefull to control type when isinstance triggers a circular import
    _CONTAINER_TYPE = "trajectory"

    def __init__(self, static_data=None):
        BaseManipulationMixin.__init__(self)
        StaticDataMixin.__init__(self, static_data)

    def _get_copy_data(self, deep):
        """
        Extract data for copy operation.

        Args:
            deep (bool): If True, create a deep copy. Default True.

        Returns:
            tuple: The extracted data to copy.
        """
        sequence_pools_copy = {**self._sequence_pools}
        settings_copy = self.settings.__class__(**self.settings.__dict__)
        static_data_copy = (
            self.static_data.copy(deep=deep) if self.static_data is not None else None
        )

        return (
            sequence_pools_copy,
            settings_copy,
            static_data_copy,
        )

    def _create_copy_instance(self, copy_data):
        """
        Create new instance with copied data.

        Args:
            copy_data (tuple): Data to copy into the new instance.

        Returns:
            Trajectory or TrajectoryPool: New instance with copied data.
        """
        sequence_pools, settings, static_data = copy_data

        # pylint: disable=E1123
        if self._is_pool:
            # TrajectoryPool case
            new_instance = self.__class__(
                sequence_pools=sequence_pools,
                settings=settings,
                static_data=static_data,
            )
        else:
            # Single Trajectory case
            new_instance = self.__class__(
                id_value=self.id_value,
                sequence_pools=sequence_pools,
                static_data=static_data,
                settings=settings,
            )

        self._propagate_t_zero(new_instance)
        return new_instance

    ## ----- ZEROING ----- ##

    def zero_from_position(self, position=0, sequence_name=None, anchor="start"):
        """
        Set t_zero based on entity position in a specific sequence.

        Args:
            position (int): Position of the entity (0-based)
            sequence_name (str): Name of the sequence to apply indexing to.
                If None, position is applied across all sequences combined.
            anchor (str): Temporal anchor point for intervals/states.
                Options: "start", "end", "middle". Not used for event sequences.

        Returns:
            self: For method chaining

        Example:
            >>> trajectory.zero_from_position(1, sequence_name="event")
        """
        settings_dict = {
            "position": position,
            "sequence_name": sequence_name,
            "anchor": anchor,
        }
        indexer = self._zeroing_base_class.init(
            settings=settings_dict, zero_setter_type="position"
        )
        indexer.assign(self)
        return self

    def zero_from_query(self, query, sequence_name, use_first=True, anchor="start"):
        """
        Set t_zero based on a query over a specific sequence.

        Args:
            query (str): Query string to filter sequence data
            sequence_name (str): Name of the sequence to apply query to
            use_first (bool): Use first matching row if True, last if False
            anchor (str): Temporal anchor point for intervals/states.
                Options: "start", "end", "middle". Not used for event sequences.

        Returns:
            self: For method chaining

        Example:
            >>> trajectory.zero_from_query("event_type == 'EMERGENCY'",
            ...                           sequence_name="event")
        """
        settings_dict = {
            "query": query,
            "sequence_name": sequence_name,
            "use_first": use_first,
            "anchor": anchor,
        }
        indexer = self._zeroing_base_class.init(
            settings=settings_dict, zero_setter_type="query"
        )
        indexer.assign(self)
        return self
