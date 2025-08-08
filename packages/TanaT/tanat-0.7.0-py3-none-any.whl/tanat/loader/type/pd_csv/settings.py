#!/usr/bin/env python3
"""
Dataframe loader settings for CSV files.
"""

from typing import Optional

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer.decorator import viewer
from pypassist.fallback.typing import Dict


@viewer
@dataclass
class PandasCSVLoaderSettings:
    """
    Settings for Pandas CSV loader

    Attributes:
        filepath: Path to the CSV file to load
        sep: Column separator used in the CSV file (comma by default)
        encoding: File encoding (utf-8 by default)
        pd_read_csv_kwargs: Additional arguments to pass to pd.read_csv
    """

    filepath: str
    sep: str = ","
    encoding: str = "utf-8"
    pd_read_csv_kwargs: Optional[Dict] = None

    def __post_init__(self):
        self.pd_read_csv_kwargs = self.pd_read_csv_kwargs or {}
