#!/usr/bin/env python3
"""
Loader configuration.
"""

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators import registry
from pypassist.dataclass.decorators.exportable.decorator import exportable
from pypassist.utils.typing import ParamDict

from .base import Loader


@registry(base_cls=Loader, register_name_attr="ltype")
@exportable(strategy="registry")
@dataclass
class LoaderConfig:
    """
    Configuration for data loading

    Attributes:
        ltype: Type of loader to use, resolved via type registry.
        settings: Loader-specific settings dictionary.

    Note:
        - ltype uses type resolution through registered loaders
        - settings must match one of the registered SETTINGS_DATACLASSES

    Example:
        ```yaml
        ltype: "csv"
        settings:
          filepath: "data/myfile.csv"
          sep: ","
        ```
    """

    ltype: str
    settings: ParamDict

    def get_loader(self):
        """
        Retrieve and instantiate a loader using the configuration.

        Returns:
            An instance of the loader configured with the provided settings.
        """
        loader_cls = Loader.get_registered(self.ltype)
        return loader_cls(settings=self.settings)
