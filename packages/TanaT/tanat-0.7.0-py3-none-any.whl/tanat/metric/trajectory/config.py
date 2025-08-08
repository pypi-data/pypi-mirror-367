#!/usr/bin/env python3
"""
Trajectory metric configuration.
"""

from typing import Optional, Union

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators import registry
from pypassist.dataclass.decorators.exportable.decorator import exportable
from pypassist.utils.typing import ParamDict

from .settings.common import CommonTrajectoryMetricSettings
from .base.metric import TrajectoryMetric
from ..config import MetricConfig


@registry(base_cls=TrajectoryMetric, register_name_attr="mtype")
@exportable(strategy="registry")
@dataclass
class TrajectoryMetricConfig(MetricConfig):
    """
    Trajectory metric configuration.

    Attributes:
        mtype:  Type of TrajectoryMetric to use, resolved via type registry.
        settings: TrajectoryMetric-specific settings dictionary.

    Note:
        - mtype uses type resolution through registered loaders
        - settings must match one of the registered SETTINGS_DATACLASSES

    Example:
        ```yaml
        mtype: "aggregation"
        settings:
            agg_fun: "mean"
        ```
    """

    settings: Optional[Union[ParamDict, CommonTrajectoryMetricSettings]] = None
