#!/usr/bin/env python3
"""
Aggregation function configuration.
"""

from typing import Optional

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators import registry
from pypassist.dataclass.decorators.exportable.decorator import exportable
from pypassist.utils.typing import ParamDict

from .base.function import AggregationFunction
from ..config import FunctionConfig


@registry(base_cls=AggregationFunction, register_name_attr="ftype")
@exportable(strategy="registry")
@dataclass
class AggregationFunctionConfig(FunctionConfig):
    """
    Aggregation function configuration.


    Attributes:
        ftype: Type of AggregationFunction to use, resolved via type registry.
        settings: AggregationFunction-specific settings dictionary.

    Note:
        - ftype uses type resolution through registered functions
        - settings must match one of the registered SETTINGS_DATACLASSES

    Example:
        ```yaml
        ftype: "mean"
        settings: null
        ```
    """

    settings: Optional[ParamDict] = None
