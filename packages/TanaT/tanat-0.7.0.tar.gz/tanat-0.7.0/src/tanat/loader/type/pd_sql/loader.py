#!/usr/bin/env python3
"""
Dataframe Loader for SQL databases.
"""

import pandas as pd
from sqlalchemy import create_engine
from pypassist.mixin.cachable import Cachable

from ...base import Loader
from .settings import PandasSQLLoaderSettings


class PandasSQLLoader(Loader, register_name="pd_sql"):
    """
    Loader for SQL databases.

    Loads data from SQL databases using pandas and SQLAlchemy.
    """

    SETTINGS_DATACLASS = PandasSQLLoaderSettings

    @Cachable.caching_method()
    def _load_impl(self, settings):
        """
        Load data from a SQL database.

        Args:
            settings: Settings for the SQL loader.

        Returns:
            pandas.DataFrame: The loaded data.
        """
        engine = create_engine(settings.conn)
        with engine.connect() as conn, conn.begin():
            data = pd.read_sql(settings.query, conn, **settings.pd_read_sql_kwargs)
        return data
