#!/usr/bin/env python3
"""
Transform settings for sequence objects.
"""

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer.decorator import viewer


@viewer
@dataclass
class TransformSettings:
    """
    Settings for data transformation.

    Attributes:
        relative_time_column: Name of the column created for relative time values.
            Default: "__RELATIVE_TIME__"
        relative_rank_column: Name of the column created for relative rank values.
            Default: "__RELATIVE_RANK__"
        occurrence_column: Name of the column created for occurrence values.
            Default: "__OCCURRENCE__"
        time_spent_column: Name of the column created for time spent values.
            Default: "__TIME_SPENT__"
        frequency_column: Name of the column created for frequency values.
            Default: "__FREQUENCY__"
        time_proportion_column: Name of the column created for time proportion values.
            Default: "__TIME_PROPORTION__"
        distribution_column: Name of the column created for distribution values.
            Default: "__DISTRIBUTION__"
    """

    relative_time_column: str = "__RELATIVE_TIME__"
    relative_rank_column: str = "__RELATIVE_RANK__"
    occurrence_column: str = "__OCCURRENCE__"
    time_spent_column: str = "__TIME_SPENT__"
    frequency_column: str = "__FREQUENCY__"
    time_proportion_column: str = "__TIME_PROPORTION__"
    distribution_column: str = "__DISTRIBUTION__"
