#!/usr/bin/env python3
"""
Settings for direct zero setter.
"""

from typing import Union
import datetime as dt

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer import viewer
from pypassist.fallback.typing import Dict


@viewer
@dataclass
class DirectZeroSetterSettings:
    """
    Settings for direct zero setter.

    Attributes:
        value: Either a datetime or a dictionary mapping IDs to datetimes.
            If a datetime, assigns the same date to all sequences/trajectories.
            If a dictionary, assigns the corresponding date to each ID.

    Note: Used for both sequence and trajectory zero setters.
    """

    value: Union[dt.datetime, Dict[str, Union[dt.datetime, None]]]

    _REGISTER_NAME = "direct"
