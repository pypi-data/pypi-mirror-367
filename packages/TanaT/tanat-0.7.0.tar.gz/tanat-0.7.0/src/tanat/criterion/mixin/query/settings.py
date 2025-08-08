#!/usr/bin/env python3
"""
Settings for query criterion.
"""

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer.decorator import viewer

from ...base.settings import Criterion
from ...decorator.entity import entity_compatible
from ...decorator.sequence import sequence_compatible


@viewer
@entity_compatible
@sequence_compatible
@dataclass
class QueryCriterion(Criterion):
    """
    Pandas-based filtering criterion for sequences and entities.

    Allows complex data filtering using pandas query syntax. Compatible with
    sequence and entity levels, enabling flexible data selection based on
    column conditions.

    Args:
        query (str): Pandas-style query string to filter data.
            Supports complex boolean conditions across columns.

    Example:
        # Filter sequences where age > 50 and gender is 'M'
        criterion = QueryCriterion(query="age > 50 and gender == 'M'")
    """

    query: str

    _REGISTER_NAME = "query"
