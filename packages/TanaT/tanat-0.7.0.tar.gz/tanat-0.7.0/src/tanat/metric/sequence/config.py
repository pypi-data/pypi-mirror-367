#!/usr/bin/env python3
"""
Sequence metric configuration.
"""

from typing import Optional, Union

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators import registry
from pypassist.dataclass.decorators.exportable.decorator import exportable
from pypassist.utils.typing import ParamDict

from .settings.base import BaseSequenceMetricSettings
from .base.metric import SequenceMetric
from ..config import MetricConfig


@registry(base_cls=SequenceMetric, register_name_attr="mtype")
@exportable(strategy="registry")
@dataclass
class SequenceMetricConfig(MetricConfig):
    """
    Sequence metric configuration.

    Attributes:
        mtype:  Type of SequenceMetric to use, resolved via type registry.
        settings: SequenceMetric-specific settings dictionary.

    Note:
        - mtype uses type resolution through registered loaders
        - settings must match one of the registered SETTINGS_DATACLASSES

    Example:
        ```yaml
        mtype: "linearpairwise"
        settings:
          entity_metric: "hamming"
          parallel: true
          workers: 4
          chunk_size: 1000
        ```
    """

    settings: Optional[Union[ParamDict, BaseSequenceMetricSettings]] = None
