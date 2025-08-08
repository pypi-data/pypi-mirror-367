#!/usr/bin/env python3
"""
Settings for position zero setter.
"""

from typing import Optional

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer import viewer

from ....time.anchor import DateAnchor


@viewer
@dataclass
class PositionZeroSetterSettings:
    """
    Settings to set T0 based on the position of an entity in the data.

    Attributes:
        position (int): The position of the entity in the sequence data (default: 0).

        anchor (DateAnchor, optional): Reference point within periods for time calculation.
            Auto-resolved by sequence type if not specified:
            - EventSequence: 'start' (events are points in time)
            - StateSequence: 'start' (beginning of state periods)
            - IntervalSequence: uses sequence settings anchor
            Override with explicit anchor for custom resolution strategy.

        sequence_name (str, optional): For trajectories only. Name of the sequence
            to use for position determination. If None, position is applied across
            all sequences combined (default: None).
    """

    position: int = 0
    anchor: Optional[DateAnchor] = None
    sequence_name: Optional[str] = None

    _REGISTER_NAME = "position"
