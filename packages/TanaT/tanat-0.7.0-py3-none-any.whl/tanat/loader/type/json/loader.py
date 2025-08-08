#!/usr/bin/env python3
"""
Loader for JSON files.
"""

import json

from pypassist.mixin.cachable import Cachable

from ...base import Loader
from .settings import JSONLoaderSettings


class JSONLoader(Loader, register_name="json"):
    """
    Loader for JSON files.

    Loads data from JSON files.
    """

    SETTINGS_DATACLASS = JSONLoaderSettings

    @Cachable.caching_method()
    def _load_impl(self, settings):
        """
        Load data from a JSON file.

        Args:
            settings: Settings for the JSON loader.

        Returns:
            dict or list: The loaded JSON data.
        """
        encoding = settings.encoding

        with open(settings.filepath, "r", encoding=encoding) as f:
            return json.load(f, **settings.json_load_kwargs)
