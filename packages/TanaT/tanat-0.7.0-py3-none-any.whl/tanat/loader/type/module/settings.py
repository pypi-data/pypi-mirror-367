#!/usr/bin/env python3
"""
Module loader settings.
"""

from typing import Optional

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer.decorator import viewer
from pypassist.fallback.typing import Dict


@viewer
@dataclass
class ModuleLoaderSettings:
    """
    Settings for Module loader

    This loader imports a Python module and calls a function from it.

    Attributes:
        module_name: Name of the Python module to import (must be installed or in PYTHONPATH)
        function_name: Name of the function to call within the module
        function_kwargs: Named arguments to pass to the function

    Example:
        ```python
        settings = ModuleLoaderSettings(
            module_name="tanat.datasets",
            function_name="load_admissions"
        )
        ```
    """

    module_name: str
    function_name: str
    function_kwargs: Optional[Dict] = None

    def __post_init__(self):
        self.function_kwargs = self.function_kwargs or {}
