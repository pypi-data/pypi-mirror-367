#!/usr/bin/env python3
"""
Entity metric configuration.
"""

from typing import Optional, Union

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators import registry
from pypassist.dataclass.decorators.exportable.decorator import exportable
from pypassist.utils.typing import ParamDict

from .settings.base import BaseEntityMetricSettings
from .base.metric import EntityMetric
from ..config import MetricConfig


@registry(base_cls=EntityMetric, register_name_attr="mtype")
@exportable(strategy="registry")
@dataclass
class EntityMetricConfig(MetricConfig):
    """
    Entity metric configuration.

    Attributes:
        mtype:  Type of EntityMetric to use, resolved via type registry.
        settings: EntityMetric-specific settings dictionary.

    Note:
        - mtype uses type resolution through registered loaders
        - settings must match one of the registered SETTINGS_DATACLASSES

    Example:
        ```yaml
        mtype: "hamming"
        settings:
            default_value: np.nan
            mode: "elementwise"
            pad_output: True
        ```
    """

    settings: Optional[Union[ParamDict, BaseEntityMetricSettings]] = None
