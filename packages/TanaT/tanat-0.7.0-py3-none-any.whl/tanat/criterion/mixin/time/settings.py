#!/usr/bin/env python3
"""
Settings for time-based filtering.
"""

from typing import Optional, Union
from datetime import datetime

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer.decorator import viewer

from ...base.settings import Criterion
from ...decorator.entity import entity_compatible
from ...decorator.sequence import sequence_compatible


@viewer
@entity_compatible
@sequence_compatible
@dataclass
class TimeCriterion(Criterion):
    """
    Flexible time-based filtering for sequences and entities.

    Enables precise temporal filtering with multiple time constraints and
    different containment modes depending on the filtering level.

    Args:
        start_before (datetime, optional):
            Filter sequences or entities starting before this timestamp.
        start_after (datetime, optional):
            Filter sequences or entities starting after this timestamp.
        end_before (datetime, optional):
            Filter sequences or entities ending before this timestamp.
        end_after (datetime, optional):
            Filter sequences or entities ending after this timestamp.
        duration_within (bool, optional):
            For entity-level filtering on state/interval entities:
            - True: Entity must be entirely contained within the time range
            - False: Entity can partially overlap with the time range
            Defaults to False. Has no effect on event entities.
        sequence_within (bool, optional):
            For sequence-level filtering (event, interval, state):
            - True: Entire sequence must be contained within the time range
            - False: Sequence can partially overlap with the time range
            Defaults to False.
        date_format (str, optional):
            Custom datetime parsing format for string inputs.

    Examples:
        # Filter entities with partial overlap (default behavior)
        TimeCriterion(
            start_after=datetime.now(),
            end_before=datetime.now() + timedelta(days=90)
        )

        # Only keep state/interval entities fully contained in time range
        TimeCriterion(
            start_after=datetime(2024, 1, 1),
            end_before=datetime(2024, 12, 31),
            duration_within=True
        )

        # Only keep sequences entirely within time range
        TimeCriterion(
            start_after=datetime(2024, 6, 1),
            end_before=datetime(2024, 6, 30),
            sequence_within=True
        )

        # Combine both strict modes
        TimeCriterion(
            start_after=datetime(2024, 1, 1),
            end_before=datetime(2024, 12, 31),
            duration_within=True,
            sequence_within=True
        )
    """

    start_before: Optional[Union[datetime, str, int]] = None
    start_after: Optional[Union[datetime, str, int]] = None
    end_before: Optional[Union[datetime, str, int]] = None
    end_after: Optional[Union[datetime, str, int]] = None
    duration_within: bool = False
    sequence_within: bool = False
    date_format: Optional[str] = None
    # TODO: add settings for duration

    _REGISTER_NAME = "time"
