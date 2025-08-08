#!/usr/bin/env python3
"""
Tanat runner configuration.
"""

from pydantic.dataclasses import dataclass

from pypassist.dataclass.decorators.runner.decorator import runner
from pypassist.dataclass.decorators.exportable.decorator import exportable
from pypassist.runner.workflow.config.base import WorkflowConfig

from .workenv.config import TanatWorkEnvConfig


@runner
@exportable(strategy="runner")
@dataclass
class TanatRunnerConfig:
    """Tanat Runner configuration."""

    workenv: TanatWorkEnvConfig
    workflow: WorkflowConfig

    def __post_init__(self):
        if isinstance(self.workenv, dict):
            self.workenv = TanatWorkEnvConfig(**self.workenv)  # pylint: disable=E1134

        if isinstance(self.workflow, dict):
            self.workflow = WorkflowConfig(**self.workflow)  # pylint: disable=E1134
