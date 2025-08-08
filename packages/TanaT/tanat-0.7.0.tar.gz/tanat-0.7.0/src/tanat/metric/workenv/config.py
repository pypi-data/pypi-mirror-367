#!/usr/bin/env python3
"""
Metric working environment.
"""


from pydantic.dataclasses import dataclass, Field

from pypassist.fallback.typing import Dict
from pypassist.dataclass.decorators.wenv.decorator import wenv
from pypassist.dataclass.decorators.exportable.decorator import exportable

from ..entity.config import EntityMetricConfig
from ..sequence.config import SequenceMetricConfig
from ..trajectory.config import TrajectoryMetricConfig


@wenv
@exportable(strategy="wenv", stem_file="workenv_defaults")
@dataclass
class MetricWorkEnvConfig:
    """
    Metric work environment.
    """

    entity: Dict[str, EntityMetricConfig] = Field(default_factory=dict)
    sequence: Dict[str, SequenceMetricConfig] = Field(default_factory=dict)
    trajectory: Dict[str, TrajectoryMetricConfig] = Field(default_factory=dict)
