#!/usr/bin/env python3
"""
Tanat working environment configuration.
"""

from pydantic.dataclasses import dataclass, Field

from pypassist.fallback.typing import Dict
from pypassist.dataclass.decorators.wenv.decorator import wenv
from pypassist.dataclass.decorators.exportable.decorator import exportable
from pypassist.mixin.cachable import CacheConfig
from pypassist.runner.workenv.custom.config.workenv import CustomWorkEnvConfig

from ...loader.config import LoaderConfig
from ...sequence.config import SequencePoolConfig
from ...trajectory.factory.config import TrajectoryPoolRunnerFactoryConfig
from ...clustering.config import ClustererConfig
from ...metric.workenv.config import MetricWorkEnvConfig
from ...function.workenv.config import FunctionWorkEnvConfig

# from ...visualization.workenv.config import VisualizationWorkEnvConfig


@wenv
@exportable(strategy="wenv")
@dataclass
class TanatWorkEnvConfig:
    """
    Tanat working environment configuration.
    """

    loaders: Dict[str, LoaderConfig] = Field(default_factory=dict)
    sequence_pools: Dict[str, SequencePoolConfig] = Field(default_factory=dict)
    trajectory_pool: TrajectoryPoolRunnerFactoryConfig = Field(
        default_factory=TrajectoryPoolRunnerFactoryConfig
    )
    metrics: MetricWorkEnvConfig = Field(default_factory=MetricWorkEnvConfig)
    functions: FunctionWorkEnvConfig = Field(default_factory=FunctionWorkEnvConfig)
    clusterers: Dict[str, ClustererConfig] = Field(default_factory=dict)
    # visualizations: VisualizationWorkEnvConfig = Field(
    #     default_factory=VisualizationWorkEnvConfig
    # )
    caching: CacheConfig = Field(default_factory=CacheConfig)
    custom_components: CustomWorkEnvConfig = Field(default_factory=CustomWorkEnvConfig)

    def __post_init__(self):
        if hasattr(super(), "__post_init__"):
            super().__post_init__()
        self.caching.apply_to_environment()
