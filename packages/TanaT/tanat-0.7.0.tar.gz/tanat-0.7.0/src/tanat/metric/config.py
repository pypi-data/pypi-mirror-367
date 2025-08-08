#!/usr/bin/env python3
"""
Common base class for metric configurations.
"""

import dataclasses
from typing import Any, Optional


@dataclasses.dataclass
class MetricConfig:
    """
    Base class for metric configurations.

    Attributes:
        mtype:  Type of metric to use, resolved via type registry.
        settings: Metric-specific settings dataclass or settings dictionary.

    Note:
        - `mtype` uses type resolution through registered metrics
        - `settings` must match one of the registered SETTINGS_DATACLASSES
    """

    mtype: str
    settings: Optional[Any] = None

    def get_metric(self, workenv=None):
        """
        Get an instance of a metric subclass.

        Args:
            workenv: Optional workenv instance.

        Returns:
            An instance of a Metric subclass with the provided settings.
        """
        # pylint: disable=no-member
        return self._REG_BASE_CLASS_.get_registered(self.mtype)(
            settings=self.settings, workenv=workenv
        )
