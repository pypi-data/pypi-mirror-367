#!/usr/bin/env python3
"""
Temporal settings for sequence objects.
"""

import dataclasses
from abc import abstractmethod


@dataclasses.dataclass
class TemporalSettings:
    """
    Base temporal configuration for sequence objects.

    Abstract base class defining temporal column requirements for different
    sequence types. Implemented by specific temporal settings classes.
    """

    @abstractmethod
    def temporal_columns(self, standardize=False):
        """
        Return the list of temporal columns.

        Args:
            standardize:
                If True, standardize the temporal columns.

        Returns:
            A list of column names.
        """
