#!/usr/bin/env python3
"""
Dataframe Loader for CSV files.
"""

import pandas as pd
from pypassist.mixin.cachable import Cachable

from ...base import Loader
from .settings import PandasCSVLoaderSettings


class PandasCSVLoader(Loader, register_name="pd_csv"):
    """
    Dataframe Loader for CSV files.

    Loads data from CSV files using pandas.
    """

    SETTINGS_DATACLASS = PandasCSVLoaderSettings

    @Cachable.caching_method()
    def _load_impl(self, settings):
        """
        Load data from a CSV file.

        Args:
            settings: Settings for the CSV loader.

        Returns:
            pandas.DataFrame: The loaded data.
        """
        return pd.read_csv(
            settings.filepath,
            sep=settings.sep,
            encoding=settings.encoding,
            **settings.pd_read_csv_kwargs,
        )
