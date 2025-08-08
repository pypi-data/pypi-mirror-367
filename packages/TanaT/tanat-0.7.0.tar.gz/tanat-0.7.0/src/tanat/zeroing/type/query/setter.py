#!/usr/bin/env python3
"""
Query zero setter.
"""

import logging

from ...setter import ZeroSetter
from ....time.query import get_date_from_query
from .settings import QueryZeroSetterSettings

LOGGER = logging.getLogger(__name__)


class QueryZeroSetter(ZeroSetter, register_name="query"):
    """
    Set sequence(s) or trajectory(s) t_zero from a query.
    Handles both single objects and pools.
    """

    SETTINGS_DATACLASS = QueryZeroSetterSettings

    def assign(self, target, **kwargs):
        """
        Assign t_zero from query-based selection.

        Args:
            target: Single sequence/trajectory or pool object
            **kwargs: Additional keyword arguments to override settings

        Returns:
            The same object with t_zero assigned
        """
        return self._set_with_anchor_resolution(target, **kwargs)

    def _handle_sequence(self, sequence_or_pool):
        """
        Handle query-based t_zero assignment for sequences.

        Args:
            sequence_or_pool: Single sequence or sequence pool

        Returns:
            t_zero value or dictionary
        """
        settings = sequence_or_pool.settings
        sequence_data = sequence_or_pool._get_standardized_data()
        temporal_columns = settings.temporal_columns(standardize=True)

        return self._extract_final_t_zeros(sequence_data, temporal_columns)

    def _handle_trajectory(self, trajectory_or_pool):
        """
        Handle query-based t_zero assignment for trajectories.

        Args:
            trajectory_or_pool: Single trajectory or trajectory pool

        Returns:
            t_zero value or dictionary
        """
        if not self.settings.sequence_name:
            raise ValueError(
                "sequence_name is required for query-based trajectory zeroing"
            )

        data_dict = self._build_data_dict(trajectory_or_pool)

        if self.settings.sequence_name not in data_dict:
            raise ValueError(
                f"Sequence '{self.settings.sequence_name}' not found. "
                f"Available sequences: {list(data_dict.keys())}"
            )

        sequence_info = data_dict[self.settings.sequence_name]
        temporal_columns = sequence_info["settings"].temporal_columns(standardize=True)
        sequence_data = sequence_info["data"]

        return self._extract_final_t_zeros(sequence_data, temporal_columns)

    def _extract_final_t_zeros(self, sequence_data, temporal_columns):
        """
        Execute query on sequence data and extract t_zeros.

        Args:
            sequence_data: The sequence data to query
            temporal_columns: List of temporal column names

        Returns:
            t_zero result (single value or dictionary)
        """
        t_zero_result = get_date_from_query(
            sequence_data=sequence_data,
            query=self.settings.query,
            temporal_columns=temporal_columns,
            anchor=self.settings.anchor,
            use_first=self.settings.use_first,
        )

        if isinstance(t_zero_result, dict) and len(t_zero_result) == 1:
            return list(t_zero_result.values())[0]

        return t_zero_result
