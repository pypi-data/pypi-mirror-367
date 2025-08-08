#!/usr/bin/env python3
"""
Loader for JSON files.
"""

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer.decorator import viewer
from pypassist.fallback.typing import Dict


@viewer
@dataclass
class JSONLoaderSettings:
    """
    Settings for JSON loader

    Attributes:
        filepath: Path to the JSON file to load
        encoding: File encoding (utf-8 by default)
        json_load_kwargs: Additional arguments to pass to json.load
    """

    filepath: str
    encoding: str = "utf-8"
    json_load_kwargs: Dict = None

    def __post_init__(self):
        self.json_load_kwargs = self.json_load_kwargs or {}
