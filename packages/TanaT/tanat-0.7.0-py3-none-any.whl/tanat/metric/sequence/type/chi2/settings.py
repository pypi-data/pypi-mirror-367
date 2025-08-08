#!/usr/bin/env python3
"""
Chi2 distances settings.
"""

from typing import Optional

from pydantic.dataclasses import dataclass

from pypassist.dataclass.decorators import viewer


@viewer
@dataclass
class Chi2MetricSettings:
    """
    Settings for the Chi2 metric.

    Attributes:
        feature_id (str):
            The feature used as state.
            If not specified, the first feature specified in
            `.settings.entity_features` is used.
    """

    feature_id: Optional[str] = None
