#!/usr/bin/env python3
"""
Hamming Entity metric settings.
"""

from typing import Optional, Union

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer.decorator import viewer
from pypassist.fallback.typing import Dict
import numpy as np

from ...settings.base import BaseEntityMetricSettings
from .....loader.base import Loader


@viewer
@dataclass
class HammingEntityMetricSettings(BaseEntityMetricSettings):
    """
    Configuration settings for the Hamming Entity metric.

    Attributes:
        default_value (float):
            Value used when cost is undefined or for padding. Defaults to `np.nan`.
        cost:
            Entity distance mapping. Can be a cost dictionary, a loader instance,
            or a string referencing a Loader in the workenv.
        mode:
            Strategy for distance computation (elementwise or allpairs).
        pad_output:
            Whether to pad elementwise output to match max input length.
    """

    default_value: float = np.nan
    pad_output: bool = True
    cost: Optional[Union[Dict, Loader, str]] = None
