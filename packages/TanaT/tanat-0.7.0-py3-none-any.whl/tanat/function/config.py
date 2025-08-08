#!/usr/bin/env python3
"""
Common base class for function configurations.
"""

import dataclasses
from typing import Optional, Any


@dataclasses.dataclass
class FunctionConfig:
    """
    Base class for all function configurations.

    Attributes:
        ftype: Type of function to use, resolved via type registry.
        settings: Function-specific settings dictionary.

    Note:
        - ftype uses type resolution through registered functions
        - settings must match one of the registered SETTINGS_DATACLASSES
    """

    ftype: str
    settings: Optional[Any] = None

    def get_function(self, workenv=None):
        """
        Get an instance of a function subclass.

        Args:
            workenv: Optional workenv instance.

        Returns:
            An instance of a Function subclass with the provided settings.
        """
        # pylint: disable=no-member
        return self._REG_BASE_CLASS_.get_registered(self.ftype)(
            settings=self.settings, workenv=workenv
        )
