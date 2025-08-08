#!/usr/bin/env python3
"""
Criterion working environment.
"""


from pydantic.dataclasses import dataclass, Field

from pypassist.fallback.typing import Dict
from pypassist.dataclass.decorators.wenv.decorator import wenv
from pypassist.dataclass.decorators.exportable.decorator import exportable

from ..sequence.config import SequenceCriterionConfig
from ..entity.config import EntityCriterionConfig
from ..trajectory.config import TrajectoryCriterionConfig


@wenv
@exportable(strategy="wenv", stem_file="workenv_defaults")
@dataclass
class CriterionWorkEnvConfig:
    """
    Criterion work environment configuration.
    """

    entity: Dict[str, EntityCriterionConfig] = Field(default_factory=dict)
    sequence: Dict[str, SequenceCriterionConfig] = Field(default_factory=dict)
    trajectory: Dict[str, TrajectoryCriterionConfig] = Field(default_factory=dict)
