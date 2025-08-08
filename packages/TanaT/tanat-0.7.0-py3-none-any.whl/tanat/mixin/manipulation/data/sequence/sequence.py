#!/usr/bin/env python3
"""
Sequence data access mixin.
"""

import logging

import pandas as pd
from pypassist.mixin.cachable import Cachable

from .....loader.base import Loader
from ..utils import (
    validate_columns,
    apply_columns,
    get_columns_to_validate,
    validate_ids,
    export_data_to_csv,
    get_empty_dataframe_like,
)
from ..exceptions import SequenceDataError
from .transform.base import SequenceDataTransformer
from .metadata import MetadataMixin

LOGGER = logging.getLogger(__name__)


class SequenceDataMixin(MetadataMixin):
    """
    Mixin for sequence data access and manipulation.
    """

    def __init__(self, sequence_data, metadata=None):
        """
        Initialize the sequence data mixin.

        Args:
            sequence_data: The sequence data (DataFrame or Loader).
        """
        self._check_sequence_data(sequence_data)
        self._sequence_data = sequence_data
        MetadataMixin.__init__(self, metadata)

        ## -- transformer
        self._transformer_base_class = SequenceDataTransformer
        self._transformer_instance = None

    @property
    def _transformer(self):
        """
        Internal property to access the correct sequence data transformer type.
        """
        if self._transformer_instance is None:
            sequence_type = self.get_registration_name()
            self._transformer_instance = SequenceDataTransformer.init(
                sequence_type, self
            )
        return self._transformer_instance

    @property
    def transformer_settings(self):
        """
        Get the settings of the sequence data transformer.
        """
        return self._transformer.settings

    def _reset_transformer(self):
        """Reset the transformer instance."""
        self._transformer_instance = None

    def _check_sequence_data(self, data):
        """
        Check the input data.
        """
        if not isinstance(data, (pd.DataFrame, Loader)):
            raise SequenceDataError(
                f"Invalid sequence data type: expected DataFrame or Loader instance, "
                f"got {type(data).__name__}."
            )

    def _get_sequence_data(self):
        """
        The sequence data with conversions applied.
        Enhanced to handle interval middle anchor sorting.
        """
        raw_data = self._get_raw_sequence_data()
        if raw_data is None:
            return None

        cols = self.settings.get_sequence_data_columns(standardize=False)
        ## Validate columns
        id_col = self.settings.id_column
        cols2validate = get_columns_to_validate(raw_data, cols, id_col)
        validate_columns(raw_data.columns, cols2validate, error_type=SequenceDataError)

        ## Handle interval middle anchor as special case
        sequence_type = self.get_registration_name()
        if (
            sequence_type == "interval"
            and str(self.settings.anchor).lower() == "middle"
        ):
            return self._apply_middle_anchor_sorting(raw_data, cols, id_col)

        ## Standard processing for all other cases
        sorting_cols = self._get_sorting_columns(raw_data)
        data = apply_columns(raw_data, cols, id_col, sorting_cols)
        return data

    def _apply_middle_anchor_sorting(self, raw_data, cols, id_col):
        """
        Apply middle anchor sorting for intervals.

        Process:
        1. Add temporary middle column
        2. Apply indexing and sorting
        3. Remove temporary column
        """
        temporal_cols = self.settings.temporal_columns()
        start_col, end_col = temporal_cols[0], temporal_cols[1]

        # Vérifier que les colonnes existent
        if start_col not in raw_data.columns or end_col not in raw_data.columns:
            LOGGER.warning(
                "Missing temporal columns for middle anchor sorting: %s, %s",
                start_col,
                end_col,
            )
            return apply_columns(
                raw_data,
                cols,
                id_col,
                [start_col] if start_col in raw_data.columns else [],
            )

        # Create copy with middle column
        data_with_middle = raw_data.copy()
        middle_col = "__TEMP_MIDDLE__"
        data_with_middle[middle_col] = (
            data_with_middle[start_col]
            + (data_with_middle[end_col] - data_with_middle[start_col]) / 2
        )

        # Apply indexing and sorting with middle column
        sorted_data = apply_columns(data_with_middle, cols, id_col, [middle_col])

        # Remove temporary column - only if it exists in final data
        if middle_col in sorted_data.columns:
            sorted_data = sorted_data.drop(columns=[middle_col])

        return sorted_data

    def _get_raw_sequence_data(self):
        """
        Get the raw sequence data without any column filtering or conversion.
        """
        data = self._sequence_data
        if isinstance(data, Loader):
            data = data.load()
            self._sequence_data = data
        return data

    @Cachable.caching_property
    def sequence_data(self):
        """
        The sequence data.
        """
        data = self._get_sequence_data()

        if self._is_pool:
            return data

        ## -- unique sequence
        return data.loc[[self.id_value]]

    def export_sequence_data(
        self,
        filepath="sequence_data.csv",
        sep=",",
        exist_ok=False,
        makedirs=False,
        **kwargs,
    ):
        """
        Export sequence data to a CSV file.

        Saves the current sequence data to a CSV file with customizable
        format options.

        Args:
            filepath (str): Path for the exported CSV file.
                Can be absolute or relative path.
            sep (str): Column separator character for CSV format.
            exist_ok (bool): Whether to overwrite existing files.
                If False, raises error if file exists.
            makedirs (bool): Whether to create parent directories.
                If True, creates missing directories in path.
            **kwargs: Additional arguments passed to pandas.to_csv().
                Common options: index=False, encoding='utf-8'

        Returns:
            pd.DataFrame: The exported sequence data (copy of original).

        Examples:
            >>> # Basic export to CSV
            >>> pool.export_sequence_data("my_sequences.csv")

            >>> # Export with custom separator and directory creation
            >>> pool.export_sequence_data(
            ...     filepath="data/sequences.tsv",
            ...     sep="\\t",
            ...     makedirs=True
            ... )

            >>> # Overwrite existing file with no index
            >>> pool.export_sequence_data(
            ...     "sequences.csv",
            ...     exist_ok=True,
            ...     index=False
            ... )
        """
        return export_data_to_csv(
            self.sequence_data,
            filepath=filepath,
            sep=sep,
            exist_ok=exist_ok,
            makedirs=makedirs,
            class_name=self.__class__.__name__,
            **kwargs,
        )

    def _get_sorting_columns(self, data):
        """
        Get columns to sort by based on sequence type and anchor configuration.

        Args:
            data: DataFrame to sort

        Returns:
            list: Columns to sort by
        """
        sequence_type = self.get_registration_name()

        if sequence_type == "event":
            return self._get_event_sorting_columns(data)
        if sequence_type == "state":
            return self._get_state_sorting_columns(data)

        # Interval sequences
        return self._get_interval_sorting_columns(data)

    def _get_event_sorting_columns(self, data):
        """Get sorting columns for event sequences."""
        time_col = self.settings.time_column
        if time_col and time_col in data.columns:
            return [time_col]
        return []

    def _get_state_sorting_columns(self, data):
        """Get sorting columns for state sequences."""
        temporal_cols = self.settings.temporal_columns()
        if temporal_cols and temporal_cols[0] in data.columns:
            return [temporal_cols[0]]  # Always sort by start time
        return []

    def _get_interval_sorting_columns(self, data):
        """Get sorting columns for intervals based on anchor configuration."""
        anchor = str(self.settings.anchor).lower()  # Convert enum to lowercase string
        temporal_cols = self.settings.temporal_columns()

        if not temporal_cols:
            return []

        start_col = temporal_cols[0]
        end_col = temporal_cols[1] if len(temporal_cols) > 1 else None

        if anchor == "start":
            return [start_col] if start_col in data.columns else []
        if anchor == "end":
            return [end_col] if end_col and end_col in data.columns else []

        # Middle anchor case
        # Return empty - middle anchor needs special processing
        return []

    def _convert_column_types(self, data_frame):
        """
        Convert data types based on metadata.

        Args:
            data_frame: data to convert.

        Returns:
            data with valid and converted columns.
        """
        # TODO: to be implemented
        return data_frame

    def _get_standardized_data(self, drop_na=False, entity_features=None):
        """
        Returns a standardized copy of the sequence data.

        Args:
            drop_na (bool): Whether to drop rows with NA values
            entity_features (list, optional): List of entity features to include.
                If None, all features specified in the sequence settings will be included.

        Returns:
            pd.DataFrame: Standardized sequence data
        """
        data_copy = self._transformer.to_standardized_data(
            drop_na, entity_features=entity_features
        ).copy()
        return data_copy

    def _get_empty_sequence_data(self):
        """Return an empty DataFrame with the same structure as sequence_data."""
        return get_empty_dataframe_like(self.sequence_data)

    def _subset_sequence_data(self, id_values):
        """
        Subset sequence data based on id values list
        """
        if self.sequence_data is None:
            return None

        valid_seq_ids = validate_ids(
            id_values, self.sequence_data.index, "sequence_data"
        )

        if not valid_seq_ids:
            LOGGER.warning(
                "No valid IDs found in sequence data. Returning empty sequence data."
            )
            return self._get_empty_sequence_data()

        return self.sequence_data.loc[valid_seq_ids]

    def to_relative_time(
        self,
        granularity,
        drop_na=False,
        entity_features=None,
    ):
        """
        Convert sequence data to relative time based on t_zero.

        Transforms temporal data to relative time units by calculating duration
        between t_zero and each entity's temporal information.

        Args:
            granularity (str): Time unit ("day", "hour", "month", etc.).
            drop_na (bool): Whether to drop rows with missing values.
            entity_features (list, optional): Features to include.
                If None, uses all features from sequence settings.

        Returns:
            pd.DataFrame: DataFrame with relative time values instead of
                original temporal columns.

        Examples:
            >>> # Set reference point and convert to days
            >>> seqpool.zero_from_position(0)
            >>> relative_data = seqpool.to_relative_time("day"))
        """
        self._safe_granularity_update(granularity)

        return self._transformer.to_relative_time(
            drop_na=drop_na,
            entity_features=entity_features,
        )

    def to_relative_rank(
        self,
        drop_na=False,
        rank_column=None,
        entity_features=None,
    ):
        """
        Convert sequence data to relative rank based on t_zero.

        Transforms temporal data to relative rank by calculating the rank of
        each entity's temporal information relative to t_zero.

        Args:
            drop_na (bool): Whether to drop rows with missing values.
            rank_column (str, optional): Column name for relative rank values.
                If None, uses default (__RELATIVE_RANK__).
            entity_features (list, optional): Features to include.
                If None, uses all features from sequence settings.

        Returns:
            pd.DataFrame: DataFrame with relative rank values (integers).
                Rank 0 corresponds to t_zero position.

        Examples:
            >>> # Set reference and get ranks
            >>> seqpool.zero_from_position(0)
            >>> rank_data = seqpool.to_relative_rank()

            >>> # Custom rank column name
            >>> seqpool.to_relative_rank(rank_column="position_from_t0")
        """
        if rank_column is not None:
            self._transformer.update_settings(relative_rank_column=rank_column)

        return self._transformer.to_relative_rank(
            drop_na=drop_na,
            entity_features=entity_features,
        )

    def _safe_granularity_update(self, granularity):
        """
        Safely update granularity in metadata & check type with pydantic dataclass.
        This method use the setter from the metadata mixin.

        Args:
            granularity (str): New granularity value

        Returns:
            None
        """
        self.granularity = granularity  # pylint: disable=W0201

    def to_occurrence(
        self,
        by_id=False,
        drop_na=False,
        occurrence_column=None,
        entity_features=None,
    ):
        """
        Count occurrences of vocabulary elements defined by entity_features.

        Args:
            by_id (bool): Whether to group by the id column.
                If True, counts per individual. If False, counts globally.
            drop_na (bool): Whether to drop rows with missing values.
            occurrence_column (str, optional): Name for occurrence column.
                If None, uses default (__OCCURRENCE__).
            entity_features (list, optional): List of entity features to count.
                If None, uses all features from sequence settings.

        Returns:
            pd.DataFrame: DataFrame with occurrence counts.

        Examples:
            >>> # Global occurrence counts
            >>> seqpool.to_occurrence()

            >>> # Occurrence counts per individual
            >>> seqpool.to_occurrence(by_id=True)

            >>> # Custom column name
            >>> seqpool.to_occurrence(occurrence_column="count")
        """
        if occurrence_column:
            self._transformer.update_settings(occurrence_column=occurrence_column)

        return self._transformer.to_occurrence(
            by_id=by_id,
            drop_na=drop_na,
            entity_features=entity_features,
        )

    def to_time_spent(
        self,
        by_id=False,
        granularity="day",
        proportion=False,
        drop_na=False,
        time_column=None,
        entity_features=None,
    ):
        """
        Compute total time spent in each entity feature.

        Args:
            by_id (bool): If True, calculates per individual.
                If False, aggregates across entire dataset.
            granularity (str): Time unit for calculation ("day", "hour", etc.).
            proportion (bool): If True, returns proportions of total time.
            drop_na (bool): Whether to drop rows with missing values.
            time_column (str, optional): Name for time spent column.
                If None, uses default (__TIME_SPENT__).
            entity_features (list, optional): Features to calculate time for.
                If None, uses all features from sequence settings.

        Returns:
            pd.DataFrame: DataFrame with time spent values.

        Examples:
            >>> # Total time spent globally in days
            >>> seqpool.to_time_spent(granularity="day")

            >>> # Time spent per individual in hours
            >>> seqpool.to_time_spent(by_id=True, granularity="hour")

            >>> # Time spent as proportions
            >>> seqpool.to_time_spent(proportion=True)
        """
        if time_column:
            self._transformer.update_settings(time_spent_column=time_column)

        return self._transformer.to_time_spent(
            by_id=by_id,
            granularity=granularity,
            proportion=proportion,
            drop_na=drop_na,
            entity_features=entity_features,
        )

    def to_occurrence_frequency(
        self,
        by_id=False,
        drop_na=False,
        frequency_column=None,
        entity_features=None,
    ):
        """
        Calculate occurrence frequency (proportion of total occurrences).

        Args:
            by_id (bool): If True, calculates frequency per individual.
                If False, calculates frequency across entire dataset.
            drop_na (bool): Whether to drop rows with missing values.
            frequency_column (str, optional): Name for frequency column.
                If None, uses default (__OCCURRENCE_FREQUENCY__).
            entity_features (list, optional): Features to calculate frequency for.
                If None, uses all features from sequence settings.

        Returns:
            pd.DataFrame: DataFrame with occurrence frequency values (0-1).

        Examples:
            >>> # Global occurrence frequencies
            >>> seqpool.to_occurrence_frequency()

            >>> # Occurrence frequencies per individual
            >>> seqpool.to_occurrence_frequency(by_id=True)
        """
        if frequency_column:
            self._transformer.update_settings(frequency_column=frequency_column)

        return self._transformer.to_occurrence_frequency(
            by_id=by_id,
            drop_na=drop_na,
            entity_features=entity_features,
        )

    def to_time_proportion(
        self,
        by_id=False,
        granularity="day",
        drop_na=False,
        proportion_column=None,
        entity_features=None,
    ):
        """
        Convert sequence data to time proportion format.

        Calculates the proportion of time spent on different activities
        within each time unit. Useful for understanding activity patterns
        over time periods.

        Args:
            by_id (bool): Whether to group results by entity ID.
                If True, calculates proportions per entity.
                If False, aggregates across all entities.
            granularity (str): Time granularity ("day", "hour", "week", etc.).
            drop_na (bool): Whether to drop rows with missing values.
            proportion_column (str, optional): Name for proportion values column.
                If None, uses default (__TIME_PROPORTION__).
            entity_features (list, optional): Features to analyze.
                If None, uses features from sequence settings.

        Returns:
            pd.DataFrame: Time proportion data with columns:
                - time_period: temporal periods
                - proportion_column: proportion values (0-1)
                - Additional columns based on grouping and features

        Examples:
            >>> # Daily time proportions per entity
            >>> state_pool.to_time_proportion(by_id=True, granularity="day")

            >>> # Weekly aggregated proportions across all entities
            >>> interval_pool.to_time_proportion(by_id=False,
            ...                                  granularity="week")

            >>> # Monthly proportions with custom column name
            >>> state_pool.to_time_proportion(
            ...     granularity="month",
            ...     proportion_column="monthly_proportion"
            ... )
        """
        if proportion_column:
            self._transformer.update_settings(proportion_column=proportion_column)

        return self._transformer.to_time_proportion(
            by_id=by_id,
            granularity=granularity,
            drop_na=drop_na,
            entity_features=entity_features,
        )

    def to_distribution(
        self,
        granularity="day",
        mode="proportion",
        time_relative=False,
        drop_na=False,
        distribution_column=None,
        entity_features=None,
    ):
        """
        Convert state sequence data to temporal distribution format.

        Creates temporal grid and calculates distribution of states within
        each time period. Only supported for state sequences.

        Args:
            granularity (str): Time granularity ("day", "hour", "week", etc.).
            mode (str): Distribution calculation mode:
                - 'proportion': Values as proportion (0-1)
                - 'percentage': Values as percentage (0-100)
                - 'count': Raw counts
            time_relative (bool): Whether to use relative time.
            drop_na (bool): Whether to drop rows with missing values.
            distribution_column (str, optional): Name for distribution column.
                If None, uses default (__DISTRIBUTION__).
            entity_features (list, optional): Features to analyze.
                If None, uses features from sequence settings.

        Returns:
            pd.DataFrame: Long format with columns:
                - time_period: temporal periods
                - annotation: state names
                - distribution_column: distribution values

        Raises:
            NotImplementedError: If called on non-state sequence types.

        Examples:
            >>> # Daily state proportions
            >>> state_pool.to_distribution(granularity='day', mode='proportion')

            >>> # Weekly state percentages
            >>> state_pool.to_distribution(granularity='week', mode='percentage')

            >>> # Relative time distribution
            >>> state_pool.zero_from_position(0)
            >>> state_pool.to_distribution(time_relative=True, mode='count')
        """
        if distribution_column:
            self._transformer.update_settings(distribution_column=distribution_column)

        return self._transformer.to_distribution(
            granularity=granularity,
            mode=mode,
            time_relative=time_relative,
            drop_na=drop_na,
            entity_features=entity_features,
        )
