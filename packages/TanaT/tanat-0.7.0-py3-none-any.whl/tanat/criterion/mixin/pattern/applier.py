#!/usr/bin/env python3
"""
Pattern criterion mixin.
"""

import logging
import re

import pandas as pd

from .settings import PatternCriterion
from .enum import PatternOperator
from .exception import InvalidColumnPatternError

LOGGER = logging.getLogger(__name__)


class PatternMatcher:
    """Helper class to encapsulate pattern matching logic."""

    def __init__(self, case_sensitive=True):
        """
        Initialize the PatternMatcher.

        Args:
            case_sensitive: Whether the pattern matching should be case-sensitive.
        """
        self.case_sensitive = case_sensitive

    def match_string_pattern(self, value, pattern):
        """
        Match a single value against a string pattern.

        Args:
            value: The value to check.
            pattern: The pattern to match against.

        Returns:
            bool: True if the value matches the pattern.
        """
        if pd.isna(value):
            return False

        value_str = str(value)
        pattern_str = str(pattern)

        # Check if the pattern is a regex
        if pattern_str.startswith("regex:"):
            regex_pattern = pattern_str[6:]  # Remove "regex:" prefix
            regex_flags = 0 if self.case_sensitive else re.IGNORECASE
            return bool(re.search(regex_pattern, value_str, regex_flags))

        # Simple substring check
        if not self.case_sensitive:
            return pattern_str.lower() in value_str.lower()
        return pattern_str in value_str

    def match_sequence_pattern(self, df, column, pattern_list):
        """
        Match a sequence pattern against a column in the dataframe.

        Args:
            df: The dataframe to match against.
            column: The column to match.
            pattern_list: The list of patterns representing a sequence.

        Returns:
            pd.Series: Boolean series indicating which rows are part of matching sequences.
        """
        pattern_mask = pd.Series(False, index=df.index)
        pattern_length = len(pattern_list)

        # Skip empty dataframes or patterns
        if df.empty or not pattern_list:
            return pattern_mask

        # For each possible starting position in the dataframe
        df_length = len(df)
        for start_idx in range(df_length):
            # Skip if we can't fit the entire pattern
            if start_idx + pattern_length > df_length:
                break

            # Get the starting row identifier
            start_id = df.index[start_idx]

            # Check if all elements in the pattern match sequentially
            if self._check_sequence_from_position(
                df, column, pattern_list, start_idx, start_id
            ):
                # Mark all positions in this matching sequence
                for i in range(pattern_length):
                    pattern_mask.iloc[start_idx + i] = True

        return pattern_mask

    def _check_sequence_from_position(
        self, df, column, pattern_list, start_idx, start_id
    ):
        """
        Check if the sequence matches starting from a given position.

        Args:
            df: The dataframe to match against.
            column: The column to match.
            pattern_list: The list of patterns representing a sequence.
            start_idx: Starting position in the dataframe.
            start_id: The starting ID value.

        Returns:
            bool: True if the sequence matches from this position.
        """
        # Check each position in the sequence
        df_index_length = len(df.index)

        for i, curr_pattern in enumerate(pattern_list):
            curr_idx = start_idx + i
            if curr_idx >= df_index_length:
                return False

            curr_id = df.index[curr_idx]

            # If we've moved to a different ID, this position can't match
            if curr_id != start_id:
                return False

            # Check if the current value matches the pattern
            curr_value = df.iloc[curr_idx][column]

            # Perform the actual pattern match
            if not self.match_string_pattern(curr_value, curr_pattern):
                return False

        return True


def match_pattern(df, patterns, case_sensitive=True, operator=PatternOperator.AND):
    """
    Match patterns in the dataframe according to the provided patterns.

    Args:
        df: The dataframe to filter.
        patterns: Dictionary of patterns for each column.
        case_sensitive: Whether pattern matching should be case-sensitive.
        operator: Logical operator to use between columns ('AND' or 'OR').

    Returns:
        pd.Series: A boolean series indicating which rows match the patterns.
    """
    # Initialize result based on the operator
    if operator == PatternOperator.AND:
        result = pd.Series(True, index=df.index)  # Start with True for AND
    else:  # OR
        result = pd.Series(False, index=df.index)  # Start with False for OR

    # If dataframe is empty or no patterns, return appropriate result
    if df.empty or not patterns:
        return result

    # Create pattern matcher
    matcher = PatternMatcher(case_sensitive)

    # Process each column's pattern
    for col, pattern in patterns.items():
        if col not in df.columns:
            LOGGER.warning("Pattern column '%s' not found in data", col)
            continue  # Skip columns that don't exist

        # Apply the appropriate pattern matching strategy
        if isinstance(pattern, list):
            # For list patterns (sequences)
            col_result = matcher.match_sequence_pattern(df, col, pattern)
        else:
            # For string/regex patterns - avoid cell-var-from-loop warning
            # by creating a local function that captures the current pattern value
            def create_matcher_function(p):
                return lambda x: matcher.match_string_pattern(x, p)

            match_func = create_matcher_function(pattern)
            col_result = df[col].apply(match_func)

        # Combine with the overall result using the specified operator
        if operator == PatternOperator.AND:
            result &= col_result
        else:  # OR
            result |= col_result

    return result


class PatternCriterionApplierMixin:
    """
    Mixin for applying pattern-based filtering to data.
    """

    SETTINGS_DATACLASS = PatternCriterion

    def validate_pattern_columns(self, data):
        """
        Validate that all pattern columns exist in the provided data.

        Args:
            data: DataFrame containing the data to validate against.

        Raises:
            InvalidColumnPatternError: If any pattern column doesn't exist in the data.
        """
        if not hasattr(self, "settings") or not hasattr(self.settings, "pattern"):
            LOGGER.warning("No pattern settings found")
            return None

        for column in self.settings.pattern:
            if column not in data.columns:
                raise InvalidColumnPatternError(
                    f"Pattern column '{column}' does not exist in the data"
                )
        return None

    def apply_pattern_matching(self, data):
        """
        Apply pattern matching to the provided data.

        Args:
            data: DataFrame to match patterns against.

        Returns:
            pd.Series: Boolean series indicating which rows match the patterns.
        """
        self.validate_pattern_columns(data)

        return match_pattern(
            data,
            self.settings.pattern,
            self.settings.case_sensitive,
            self.settings.operator,
        )
