#!/usr/bin/env python3
"""
Loader for Python script files.
"""

import importlib.util
import os

from pypassist.mixin.cachable import Cachable

from ...base import Loader
from .settings import ScriptLoaderSettings


class ScriptLoader(Loader, register_name="script"):
    """
    Loader for Python script files.

    Executes a Python script file and calls a function from it.
    The script file is loaded dynamically at runtime.
    """

    SETTINGS_DATACLASS = ScriptLoaderSettings

    @Cachable.caching_method()
    def _load_impl(self, settings):
        """
        Execute a Python script file and call a function from it.

        Args:
            settings: Settings for the Script File loader.

        Returns:
            Any: The result of the function call

        Raises:
            FileNotFoundError: If the script file cannot be found
            AttributeError: If the function is not found in the script
            TypeError: If the function is not callable
        """
        if not os.path.exists(settings.script_path):
            raise FileNotFoundError(f"Script file not found: {settings.script_path}")

        module_file = os.path.basename(settings.script_path)
        module_name = os.path.splitext(module_file)[0]

        spec = importlib.util.spec_from_file_location(module_name, settings.script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Get the function from the module
        if not hasattr(module, settings.function_name):
            raise AttributeError(
                f"Function {settings.function_name} not found in script {module_name}"
            )

        function = getattr(module, settings.function_name)
        if not callable(function):
            raise TypeError(
                f"{settings.function_name} in script {module_name} is not callable"
            )

        # Call the function
        return function(**settings.function_kwargs)
