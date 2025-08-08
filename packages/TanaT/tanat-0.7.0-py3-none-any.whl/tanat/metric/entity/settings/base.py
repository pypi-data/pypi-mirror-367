#!/usr/bin/env python3
"""
Base class for entity metric settings.
"""

from pydantic.dataclasses import dataclass

from ..base.enum import EntityMetricMode


@dataclass
class BaseEntityMetricSettings:
    """
    Base class for entity metric settings.
    """

    mode: EntityMetricMode = EntityMetricMode.ELEMENTWISE
