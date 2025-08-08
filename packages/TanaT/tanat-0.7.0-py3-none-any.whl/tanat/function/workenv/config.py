#!/usr/bin/env python3
"""
Function working environment.
"""


from pydantic.dataclasses import dataclass, Field

from pypassist.fallback.typing import Dict
from pypassist.dataclass.decorators.wenv.decorator import wenv
from pypassist.dataclass.decorators.exportable.decorator import exportable

from ..aggregation.config import AggregationFunctionConfig


@wenv
@exportable(strategy="wenv", stem_file="workenv_defaults")
@dataclass
class FunctionWorkEnvConfig:
    """
    Function work environment.
    """

    aggregation: Dict[str, AggregationFunctionConfig] = Field(default_factory=dict)
