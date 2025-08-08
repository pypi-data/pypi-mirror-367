#!/usr/bin/env python3
"""
User data access utils.
"""

from .zenodo import ZenodoAccessor


def access(data_type, cache_dir=None, force=False):
    """
    Access a dataset from Zenodo and return a ready-to-use object.

    Depending on the type, this may return:
    - a DataFrame (for file-based datasets: CSV, Parquet, etc.)
    - a database connection (for SQL-based datasets)

    Data is cached locally after the first download unless `force=True` is set.

    Args:
        data_type (str): Name of the dataset registered in ZenodoAccessor.
        cache_dir (str, optional): Directory used for caching. Defaults to system temp directory.
        force (bool): If True, forces re-download even if data is already cached.

    Returns:
        A usable object for interacting with the dataset.

    Raises:
        ValueError: If `data_type` is not registered in the accessor.

    Examples:
        >>> # Access a MVAD CSV dataset as a DataFrame
        >>> df = access("mvad")

        >>> # Access a SQL database as a connection
        >>> conn = access("mimic4")
    """
    accessor = ZenodoAccessor.init(data_type, cache_dir=cache_dir)
    return accessor.get(force=force)
