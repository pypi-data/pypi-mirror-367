#!/usr/bin/env python3
"""
Loader for Python modules.
"""

import importlib

from pypassist.mixin.cachable import Cachable

from ...base import Loader
from .settings import ModuleLoaderSettings


class ModuleLoader(Loader, register_name="module"):
    """
    Loader for Python modules.

    Imports a Python module and calls a function from it.
    The module must be installed or in the Python path.
    """

    SETTINGS_DATACLASS = ModuleLoaderSettings

    @Cachable.caching_method()
    def _load_impl(self, settings):
        """
        Import a module and call a function from it.

        Args:
            settings: Settings for the Module loader.

        Returns:
            Any: The result of the function call

        Raises:
            ImportError: If the module cannot be imported
            AttributeError: If the function is not found in the module
            TypeError: If the function is not callable
        """
        try:  # Try to import the module
            module = importlib.import_module(settings.module_name)
        except ImportError as err:
            raise ImportError(
                f"Module {settings.module_name} could not be imported"
            ) from err

        # Get the function from the module
        if not hasattr(module, settings.function_name):
            raise AttributeError(
                f"Function {settings.function_name} not found in module {settings.module_name}"
            )

        function = getattr(module, settings.function_name)
        if not callable(function):
            raise TypeError(
                f"{settings.function_name} in module {settings.module_name} is not callable"
            )
        return function(**settings.function_kwargs)
