#!/usr/bin/env python3
"""
Position zero setter.
"""

import logging
import pandas as pd

from ...setter import ZeroSetter
from ....time.anchor import resolve_date_series_from_anchor
from .settings import PositionZeroSetterSettings

LOGGER = logging.getLogger(__name__)


class PositionZeroSetter(ZeroSetter, register_name="position"):
    """
    Set sequence(s) or trajectory(s) t_zero from entity at a given position.
    Handles both single objects and pools.
    """

    SETTINGS_DATACLASS = PositionZeroSetterSettings
    CANDIDATES_COLUMN = "__T0_CANDIDATES__"

    def assign(self, target, **kwargs):
        """
        Assign t_zero from position-based selection.

        Args:
            target: Single sequence/trajectory or pool object
            **kwargs: Additional keyword arguments to override settings

        Returns:
            The same object with t_zero assigned
        """
        return self._set_with_anchor_resolution(target, **kwargs)

    def _handle_sequence(self, sequence_or_pool):
        """
        Handle position-based t_zero assignment for sequences.

        Args:
            sequence_or_pool: Single sequence or sequence pool

        Returns:
            t_zero value or dictionary
        """
        sequence_data = sequence_or_pool._get_standardized_data()
        if len(sequence_data) == 0:
            LOGGER.warning("Empty sequence. Returning None.")
            return None

        settings = sequence_or_pool.settings
        temporal_columns = settings.temporal_columns(standardize=True)

        # Resolve dates from anchor
        sequence_data[self.CANDIDATES_COLUMN] = resolve_date_series_from_anchor(
            sequence_data, temporal_columns, self.settings.anchor
        )
        sequence_data.drop(columns=temporal_columns, inplace=True)

        return self._extract_final_t_zeros(sequence_data, [self.CANDIDATES_COLUMN])

    def _handle_trajectory(self, trajectory_or_pool):
        """
        Handle position-based t_zero assignment for trajectories.

        Args:
            trajectory_or_pool: Single trajectory or trajectory pool

        Returns:
            t_zero value or dictionary
        """
        if self.settings.sequence_name:
            return self._position_from_specific_sequence(trajectory_or_pool)
        return self._position_from_all_sequences(trajectory_or_pool)

    def _position_from_specific_sequence(self, trajectory_or_pool):
        """
        Extract t_zero from a specific sequence in trajectory.

        Args:
            trajectory_or_pool: Trajectory or trajectory pool

        Returns:
            t_zero value or dictionary
        """
        data_dict = self._build_data_dict(trajectory_or_pool)

        if self.settings.sequence_name not in data_dict:
            raise ValueError(
                f"Sequence '{self.settings.sequence_name}' not found. "
                f"Available sequences: {list(data_dict.keys())}"
            )

        sequence_info = data_dict[self.settings.sequence_name]
        candidates = self._extract_sequence_candidates(sequence_info)
        candidates_df = candidates.to_frame(name=self.CANDIDATES_COLUMN)

        return self._extract_final_t_zeros(candidates_df, [self.CANDIDATES_COLUMN])

    def _position_from_all_sequences(self, trajectory_or_pool):
        """
        Extract t_zero from all sequences combined in trajectory.

        Args:
            trajectory_or_pool: Trajectory or trajectory pool

        Returns:
            t_zero value or dictionary
        """
        data_dict = self._build_data_dict(trajectory_or_pool)
        candidates = self._collect_time_candidates(data_dict)

        return self._extract_final_t_zeros(candidates, [self.CANDIDATES_COLUMN])

    def _collect_time_candidates(self, data_dict):
        """Collect and sort time candidates from all sequences."""
        candidates_list = []

        for sequence_info in data_dict.values():
            candidates = self._extract_sequence_candidates(sequence_info)
            candidates_list.append(candidates)

        return self._combine_candidates(candidates_list)

    def _extract_sequence_candidates(self, sequence_info):
        """Extract time candidates from a single sequence."""
        seq_data = sequence_info["data"]
        settings = sequence_info["settings"]
        temporal_columns = settings.temporal_columns(standardize=True)

        return resolve_date_series_from_anchor(
            seq_data, temporal_columns, self.settings.anchor
        )

    def _combine_candidates(self, candidates_list):
        """Combine and sort all candidates into a single DataFrame."""
        return (
            pd.concat(candidates_list)
            .sort_values(kind="mergesort")
            .sort_index(kind="mergesort")
            .to_frame(name=self.CANDIDATES_COLUMN)
        )

    def _extract_final_t_zeros(self, sequence_data, t_zero_candidates_column):
        """
        Find and extract t_zeros from sequence data.

        Args:
            sequence_data: The pooled sequence data
            t_zero_candidates_column: T0 candidates column name

        Returns:
            Dictionary mapping sequence IDs to t_zero values or single value
        """
        t_zeros = sequence_data.groupby(sequence_data.index).apply(
            lambda group: self._extract_t_zero_from_group(
                group, t_zero_candidates_column[0]
            )
        )
        if len(t_zeros) == 1:
            return t_zeros.values[0]
        return t_zeros.to_dict()

    def _extract_t_zero_from_group(self, seq_group, t_zero_candidates_column):
        """
        Extract t_zero from a sequence group or single sequence.

        Args:
            seq_group: The sequence data (single sequence or group)
            t_zero_candidates_column: T0 candidates column name

        Returns:
            The t_zero value or None if extraction fails
        """
        if len(seq_group) == 0:
            return None

        if not self._is_position_valid(seq_group):
            self._log_position_out_of_bounds_warning(seq_group)
            return None

        temporal_value = seq_group.iloc[self.settings.position][
            t_zero_candidates_column
        ]
        return temporal_value

    def _is_position_valid(self, seq_group):
        """
        Check if the configured position is valid for the sequence group.
        Supports negative indices to access from the end.

        Args:
            seq_group: The sequence group to validate

        Returns:
            bool: True if position is valid
        """
        seq_len = len(seq_group)
        return -seq_len <= self.settings.position < seq_len

    def _log_position_out_of_bounds_warning(self, seq_group):
        """
        Log a warning when position is out of bounds.

        Args:
            seq_group: The sequence group that caused the error
        """
        sequence_id = seq_group.index[0] if len(seq_group) > 0 else "Unknown"
        LOGGER.warning(
            "sequence ID %s: Position %s out of bounds. Returning None.",
            sequence_id,
            self.settings.position,
        )
