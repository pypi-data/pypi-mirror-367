#!/usr/bin/env python3
"""
Settings for static criterion.
"""

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer.decorator import viewer

from ...base.settings import Criterion
from ...decorator.sequence import sequence_compatible
from ...decorator.trajectory import trajectory_compatible


@viewer
@sequence_compatible
@trajectory_compatible
@dataclass
class StaticCriterion(Criterion):
    """
    Filter sequences and trajectories based on static metadata.

    Enables complex filtering using pandas query syntax on
    static features like demographics, patient characteristics,
    or other time-invariant attributes.

    Args:
        query (str):
            Pandas-style query string to filter static data.
            Supports complex boolean conditions across static columns.

    Example:
        # Filter for elderly patients with chronic conditions
        StaticCriterion(query="age > 50 and chronic_condition == True")
    """

    query: str

    _REGISTER_NAME = "static"
