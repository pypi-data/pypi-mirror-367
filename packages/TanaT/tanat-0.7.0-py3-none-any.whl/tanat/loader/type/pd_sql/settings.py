#!/usr/bin/env python3
"""
Dataframe Loader Settings for SQL databases.
"""

from typing import Optional

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer.decorator import viewer
from pypassist.fallback.typing import Dict


@viewer
@dataclass
class PandasSQLLoaderSettings:
    """
    Settings for SQL loader

    Attributes:
        conn: SQLAlchemy connection string (e.g., 'sqlite:///database.db')
        query: SQL query to execute
        pd_read_sql_kwargs: Additional arguments to pass to pd.read_sql
    """

    conn: str
    query: str
    pd_read_sql_kwargs: Optional[Dict] = None

    def __post_init__(self):
        self.pd_read_sql_kwargs = self.pd_read_sql_kwargs or {}
