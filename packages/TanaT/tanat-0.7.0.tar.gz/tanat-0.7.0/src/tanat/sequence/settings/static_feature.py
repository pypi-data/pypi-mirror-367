#!/usr/bin/env python3
"""
Static feature settings for sequence objects.
"""

import dataclasses
from typing import Optional

from pypassist.fallback.typing import List


@dataclasses.dataclass
class StaticFeatureSettings:
    """
    Static feature configuration for sequence objects.

    Manages static features that remain constant across time for each
    sequence (demographics, categories, etc.). Optional configuration
    for sequences without static data.

    Attributes:
        static_features (Optional[List[str]]): Column names for static
            features. None if no static features are available.
    """

    static_features: Optional[List[str]] = None
