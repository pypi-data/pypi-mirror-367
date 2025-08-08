#!/usr/bin/env python3
"""
Static data access mixin.
"""

import logging

import pandas as pd
from pypassist.mixin.cachable import Cachable

from ....loader.base import Loader
from .utils import (
    validate_columns,
    apply_columns,
    get_columns_to_validate,
    is_already_indexed,
    validate_ids,
    export_data_to_csv,
    get_empty_dataframe_like,
)
from .exceptions import StaticDataError

LOGGER = logging.getLogger(__name__)


class StaticDataMixin:
    """
    Mixin for static data access and manipulation.
    """

    def __init__(self, static_data=None):
        """
        Initialize the static data mixin.

        Args:
            static_data: The static data (DataFrame or Loader).
        """
        if static_data is not None:
            self._check_static_data(static_data)
        self._static_data = static_data

    def _check_static_data(self, data):
        """
        Check the static feature data.
        """
        if not isinstance(data, (pd.DataFrame, Loader)):
            raise StaticDataError(
                f"Invalid data type: expected DataFrame or Loader, got {type(data).__name__}."
            )

        if self.settings.static_features is None:
            raise StaticDataError("Missing static feature list in settings.")

    def _get_static_data(self):
        """
        Get static data with indexing applied.
        """
        raw_static_data = self._get_raw_static_data()
        if raw_static_data is None:
            return None

        cols = self.settings.static_features

        # Validate columns
        id_col = self.settings.id_column
        cols2validate = get_columns_to_validate(raw_static_data, cols, id_col)
        validate_columns(
            raw_static_data.columns, cols2validate, error_type=StaticDataError
        )

        # Apply indexing & extract columns
        return apply_columns(raw_static_data, cols, id_col)

    def _get_raw_static_data(self):
        """
        Get the raw static feature data without any filtering or conversion.
        """
        static_data = self._static_data
        if static_data is None:
            return None

        if isinstance(static_data, Loader):
            # Loader instance
            static_data = static_data.load()
            self._static_data = static_data

        return static_data

    @Cachable.caching_property
    def static_data(self):
        """
        The static feature data.
        """
        if self._static_data is None:
            return None

        data = self._get_static_data()
        if self._is_pool:
            return data

        ## -- unique container
        return data.loc[[self.id_value]]

    def add_static_features(
        self,
        static_data,
        id_column=None,
        static_features=None,
        override=False,
    ):
        """
        Add static feature data. If static_data is already set it will be joined.

        Args:
            static_data (pd.DataFrame): The static feature data.
            id_column (str, optional): The column containing the ID values. Defaults to None.
                If None, the id_column is expected to be specified in settings.id_column.
            static_features (list, optional): List of static feature names. Defaults to None.
                If None all columns except id_column will be added to settings.static_features.
            override (bool, optional): Whether to override existing values on conflict.
                Defaults to False.

        Returns:
            self : For method chaining

        Raises:
            StaticDataError: If static_data is not a DataFrame, if id_column is not specified,
                or if required columns are missing.
        """

        id_column = self._resolve_id_column(id_column)
        static_data, static_features = self._validate_and_extract_columns(
            static_data, id_column, static_features
        )

        self._safe_static_data_merge(static_data, id_column, static_features, override)

        self._update_static_settings(id_column, static_features)
        self.clear_cache()
        return self

    def clear_static_data(self):
        """
        Clear all static data and reset related states.

        Returns:
            self: For method chaining
        """
        self._static_data = None
        # pylint: disable=no-member
        self.settings.reset_static_settings()
        self.clear_cache()
        return self

    def get_static_feature(self, feature_name):
        """
        Return a given feature from the static feature data.
        """
        if self.static_data is None:
            return None

        if feature_name not in self.settings.static_features:
            raise StaticDataError(
                f"Static feature '{feature_name}' not found in static data."
            )
        return self.static_data[feature_name]

    def drop_static_features(self, list_features):
        """
        Remove specified static features from the dataset.

        Args:
            list_features (list or str): Feature(s) to remove.
                Can be a single feature name or a list of feature names.

        Returns:
            self: For method chaining

        Raises:
            StaticDataError: If any of the features do not exist or cannot be dropped.
        """
        if self._static_data is None:
            LOGGER.info(
                "%s: No static data loaded. Nothing to drop.", self.__class__.__name__
            )
            return self

        features_to_drop = (
            [list_features] if not isinstance(list_features, list) else list_features
        )

        if not features_to_drop:
            return self

        # pylint: disable=no-member
        current_features = self.settings.static_features or []
        missing_features = [f for f in features_to_drop if f not in current_features]

        if missing_features:
            raise StaticDataError(
                f"Cannot drop non-existent static features: {missing_features}"
            )

        updated_features = [f for f in current_features if f not in features_to_drop]
        self.update_settings(static_features=updated_features)

        columns_to_drop = [
            f for f in features_to_drop if f in self._static_data.columns
        ]
        if columns_to_drop:
            self._static_data = self._static_data.drop(columns=columns_to_drop)

        self.clear_cache()
        return self

    def export_static_data(
        self,
        filepath="static_data.csv",
        sep=",",
        exist_ok=False,
        makedirs=False,
        **kwargs,
    ):
        """
        Export the static feature data to a CSV file.

        Args:
            filepath (str, optional): Path to save the exported CSV file.
                Defaults to "static_data.csv".
            sep (str, optional): Separator for the CSV file. Defaults to ",".
            exist_ok (bool, optional): Whether to overwrite existing file.
                Defaults to False.
            makedirs (bool, optional): Whether to create parent directories.
                Defaults to False.
            **kwargs: Additional arguments for `pandas.to_csv()`.

        Returns:
            pd.DataFrame or None: The exported static data, or None if no data is available.
        """
        return export_data_to_csv(
            self.static_data,
            filepath=filepath,
            sep=sep,
            exist_ok=exist_ok,
            makedirs=makedirs,
            class_name=self.__class__.__name__,
            **kwargs,
        )

    def _safe_static_data_merge(self, new_data, id_column, static_features, override):
        """
        Merge new static data safely, handling value conflicts.
        Uses outer join to include all IDs from both datasets.

        Args:
            new_data (pd.DataFrame): The new static data to merge.
            id_column (str): The column to join on.
            static_features (list): List of feature columns to add.
            override (bool): Whether to override existing values on conflict.

        Raises:
            StaticDataError: If conflicting values exist and override is False.
        """
        if self._static_data is None:
            self._static_data = new_data
            return None

        current_data = (
            self._static_data.reset_index()
            if is_already_indexed(self._static_data, id_column)
            else self._static_data.copy()
        )

        merged_data = pd.merge(
            current_data, new_data, on=id_column, how="outer", suffixes=("", "_new")
        )

        for col in static_features:
            new_col = f"{col}_new"
            if new_col in merged_data.columns:
                # Detect conflicts
                conflict_mask = (
                    merged_data[col].notna()
                    & merged_data[new_col].notna()
                    & (merged_data[col] != merged_data[new_col])
                )

                if conflict_mask.any():
                    if not override:
                        raise StaticDataError(
                            f"Conflicting values found for column '{col}' on some IDs. "
                            "Set override=True to overwrite them."
                        )
                    merged_data.loc[conflict_mask, col] = merged_data.loc[
                        conflict_mask, new_col
                    ]

                # Combine
                merged_data[col] = merged_data[col].combine_first(merged_data[new_col])
                merged_data.drop(columns=[new_col], inplace=True)

        self._static_data = merged_data
        self.clear_cache()
        return None

    def _resolve_id_column(self, id_column):
        """Resolve the ID column name."""
        if id_column is None:
            id_column = self.settings.id_column

        if id_column is None:
            raise StaticDataError(
                "id_column not specified neither in call nor in settings."
            )
        return str(id_column)

    def _validate_and_extract_columns(self, data, id_column, feature_columns=None):
        """
        Validates and extracts the specified columns from the data.

        Args:
            data (pd.DataFrame): The dataframe to validate and extract from
            id_column (str): The ID column name
            feature_columns (list, optional): List of feature columns to extract.
                If None, all columns except id_column will be used.

        Returns:
            tuple: (filtered_data, feature_columns)
        """
        # Ensure data is a DataFrame
        if not isinstance(data, pd.DataFrame):
            raise StaticDataError(
                f"Invalid data type: expected DataFrame, got {type(data).__name__}."
            )

        if is_already_indexed(data, id_column):
            data = data.reset_index(drop=False)

        provided_columns = data.columns.tolist()

        # If no feature columns specified, use all except ID column
        if feature_columns is None:
            feature_columns = [col for col in provided_columns if col != id_column]
        elif not isinstance(feature_columns, list):
            feature_columns = [feature_columns]

        # Validate all required columns are present
        validate_columns(
            provided_columns,
            [id_column] + feature_columns,
            error_type=StaticDataError,
        )

        # Return both the filtered data and the feature column list
        return data[[id_column] + feature_columns], feature_columns

    def _update_static_settings(self, id_column, static_features):
        """
        Update static settings.
        """
        # pylint: disable=no-member
        if self.settings.id_column is None:
            self.update_settings(id_column=id_column)

        existing = self.settings.static_features or []
        new_features = [f for f in static_features if f not in existing]
        self.update_settings(static_features=existing + new_features)

    def _get_empty_static_data(self):
        """Return an empty DataFrame with the structure of static_data."""
        return get_empty_dataframe_like(self.static_data)

    def _subset_static_data(self, id_values):
        """
        Subset static data based on list of id_values
        """
        if self.static_data is None:
            return None

        valid_static_ids = validate_ids(
            id_values, self.static_data.index, "static_data"
        )

        if not valid_static_ids:
            LOGGER.warning(
                "No valid IDs found in static data. Returning empty static_data."
            )
            return self._get_empty_static_data()

        return self.static_data.loc[valid_static_ids]
