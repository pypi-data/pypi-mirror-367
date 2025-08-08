#!/usr/bin/env python3
"""
Base criterion configuration.
"""

import dataclasses
from typing import Union

from pypassist.utils.typing import ParamDict

from .base.settings import Criterion


@dataclasses.dataclass
class CriterionConfig:
    """
    Base criterion configuration.

    Attributes:
        criterion_type: Type of criterion, resolved via type registry.
        settings: Criterion-specific settings dictionary.
    """

    settings: Union[ParamDict, Criterion]
    criterion_type: str

    def get_criterion(self):
        """Get criterion instance."""
        # pylint: disable=no-member
        return self._REG_BASE_CLASS_.init(
            criterion_type=self.criterion_type, settings=self.settings
        )
