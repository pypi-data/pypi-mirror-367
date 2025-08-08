#!/usr/bin/env python3
"""
Script File loader settings.
"""

from typing import Optional

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer.decorator import viewer
from pypassist.fallback.typing import Dict


@viewer
@dataclass
class ScriptLoaderSettings:
    """
    Settings for Script loader

    This loader executes a Python script file and calls a function defined in that script.

    Attributes:
        script_path: Path to the Python script file to execute
        function_name: Name of the function to call within the script
        function_kwargs: Named arguments to pass to the function

    Example:
        ```python
        settings = ScriptFileLoaderSettings(
            script_path="/path/to/script.py",
            function_name="load_data",
            function_kwargs={"param1": "value1"}
        )
        ```
    """

    script_path: str
    function_name: str
    function_kwargs: Optional[Dict] = None

    def __post_init__(self):
        self.function_kwargs = self.function_kwargs or {}
