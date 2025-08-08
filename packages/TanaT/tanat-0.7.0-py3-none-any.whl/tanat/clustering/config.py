#!/usr/bin/env python3
"""
Clustering configuration.
"""

from typing import Optional

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators import registry
from pypassist.dataclass.decorators.exportable.decorator import exportable
from pypassist.utils.typing import ParamDict

from .clusterer import Clusterer


@registry(base_cls=Clusterer, register_name_attr="ctype")
@exportable(strategy="registry")
@dataclass
class ClustererConfig:
    """
    Base class for all clustering configurations.

    Attributes:
        ctype: Type of clustering algorithm to use, resolved via type registry.
        settings: Clustering algorithm-specific settings dictionary.

    Note:
        - ctype uses type resolution through registered clustering algorithms
        - settings must match one of the registered SETTINGS_DATACLASSES

    Example:
        ```yaml
        ctype: "hierarchical"
        settings:
            metric: "linearpairwise"
            n_clusters: 5
        ```
    """

    ctype: str
    settings: Optional[ParamDict] = None

    def get_clusterer(self, workenv=None):
        """
        Retrieve and instantiate a Clusterer.

        Args:
            workenv: Optional working env instance.

        Returns:
            An instance of the Clusterer configured
            with the provided settings.
        """
        return Clusterer.get_registered(self.ctype)(
            settings=self.settings, workenv=workenv
        )
