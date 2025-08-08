#!/usr/bin/env python3
"""
Settings for query zero setter.
"""

from typing import Optional

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer import viewer

from ....time.query import QueryDateResolverSettings


@viewer
@dataclass
class QueryZeroSetterSettings(QueryDateResolverSettings):
    """
    Settings for assigning index dates based on a query over data.

    This setter extracts an index date from one or more rows selected via a query.

    Attributes:
        query (str): A query string used to select relevant rows from the data.
            Can refer to any valid field (e.g. "event == 'hospitalization'").

        anchor (DateAnchor, optional): Reference point within periods for time calculation.
            Auto-resolved by sequence type if not specified:
            - EventSequence: 'start' (events are points in time)
            - StateSequence: 'start' (beginning of state periods)
            - IntervalSequence: uses sequence settings anchor
            Override with explicit anchor for custom resolution strategy.

        use_first (bool): If True, selects the first matching row; otherwise, uses the last.

        sequence_name (str, optional): For trajectories only. Name of the sequence
            on which to apply the query. Required for trajectory objects.
    """

    sequence_name: Optional[str] = None

    _REGISTER_NAME = "query"
