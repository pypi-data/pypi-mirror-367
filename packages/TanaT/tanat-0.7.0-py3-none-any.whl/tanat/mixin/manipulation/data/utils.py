#!/usr/bin/env python3
"""
Utility functions for data access mixins.
"""

import logging

import pandas as pd
from pypassist.utils.export import export_to_csv

LOGGER = logging.getLogger(__name__)


def validate_columns(
    actual_columns,
    expected_columns,
    error_type=ValueError,
    context=None,
):
    """
    Validate that all expected columns are present in the actual columns.

    Args:
        actual_columns (list or pandas.Index): The actual columns present in the data.
        expected_columns (list): The columns that are expected to be present.
        error_type (Exception, optional): Type of exception to raise on error.
            Defaults to ValueError.
        context (str, optional): Context description for error message, e.g. "static feature data".
            Makes error messages more specific to the calling context.

    Returns:
        bool: True if validation passes (all expected columns are present).

    Raises:
        error_type: If any expected column is missing, with a context-specific message.
    """
    if not isinstance(actual_columns, (list, set)):
        actual_columns = list(actual_columns)

    missing_columns = set(expected_columns) - set(actual_columns)
    if missing_columns:
        context_msg = f" from {context}" if context else ""
        raise error_type(
            f"The following columns are missing{context_msg}: {', '.join(missing_columns)}"
        )

    return True


def is_already_indexed(data_frame, id_column):
    """
    Check if DataFrame is already indexed by id_column.

    Args:
        data_frame: DataFrame to check
        id_column: Name of the ID column

    Returns:
        bool: True if already indexed, False otherwise
    """
    return data_frame.index.name == id_column


def get_columns_to_validate(data_frame, cols, id_column):
    """
    Get columns that need validation based on indexing status.

    Args:
        data_frame: DataFrame to check
        cols: List of columns to select
        id_column: Name of the ID column

    Returns:
        list: Columns to validate
    """
    if not isinstance(cols, list):
        cols = list(cols)

    if not is_already_indexed(data_frame, id_column):
        return cols

    # If already indexed, exclude the ID column from validation
    return [c for c in cols if c != id_column]


def apply_columns(data_frame, cols, id_column, sorting_columns=None):
    """
    Obtain a view of the data containing the specified cols after
    applying indexing and optional sorting.

    Args:
        data_frame: Data to select columns from.
        cols: Columns to select.
        id_column: Name of the ID column.
        sorting_columns (list, optional): Columns to sort by. Defaults to None.

    Returns:
        DataFrame with selected columns and proper indexing.
    """
    if data_frame.empty and id_column not in data_frame.columns:
        data_frame.index = pd.Index([], name=id_column)

    elif data_frame.index.name != id_column:
        data_frame = data_frame.set_index(id_column)

    data_frame = data_frame.sort_index()

    if sorting_columns:
        valid_sorting = [col for col in sorting_columns if col in data_frame.columns]
        if valid_sorting:
            data_frame = data_frame.groupby(level=0, group_keys=False).apply(
                lambda x: x.sort_values(by=valid_sorting)
            )

    selected_cols = [
        col for col in cols if col != id_column and col in data_frame.columns
    ]
    return data_frame[selected_cols]


def validate_ids(requested, available_index, label="data"):
    """Validate and filter ID values against a reference index."""
    requested_set = set(requested)
    available_set = set(available_index)
    valid_ids = sorted(available_set & requested_set)
    missing_ids = requested_set - available_set

    if missing_ids:
        preview = sorted(missing_ids)[:5]
        suffix = "..." if len(missing_ids) > 5 else ""
        LOGGER.warning(
            "%s ID(s) not found in %s and will be ignored: %s%s",
            len(missing_ids),
            label,
            preview,
            suffix,
        )
    return valid_ids


def export_data_to_csv(
    data,
    filepath,
    sep=",",
    exist_ok=False,
    makedirs=False,
    class_name="DataMixin",
    **kwargs,
):
    """
    Utility function to export data to CSV file.

    Args:
        data: The data to export.
        filepath (str): Path to save the exported CSV file.
        sep (str, optional): Separator for the CSV file. Defaults to ",".
        exist_ok (bool, optional): Whether to overwrite existing file. Defaults to False.
        makedirs (bool, optional): Whether to create parent directories. Defaults to False.
        class_name (str): Name of the calling class for logging.
        **kwargs: Additional arguments for `pandas.to_csv()`.

    Returns:
        pd.DataFrame: The exported data.
    """
    if data is None:
        LOGGER.info("%s: No data to export. Skipping.", class_name)
        return None

    export_to_csv(
        data,
        filepath=filepath,
        sep=sep,
        exist_ok=exist_ok,
        makedirs=makedirs,
        **kwargs,
    )

    LOGGER.info(
        "%s: Data successfully exported to `%s`.",
        class_name,
        filepath,
    )

    return data


def get_empty_dataframe_like(data):
    """
    Return an empty DataFrame with the same structure as the input data.

    Args:
        data: DataFrame to mimic structure from.

    Returns:
        pd.DataFrame: Empty DataFrame with same structure.
    """
    if data is not None:
        return data.iloc[0:0]
    return None
