#!/usr/bin/env python3
"""
Generic custom exceptions.
"""

import logging

import yaml
import pandas as pd

LOGGER = logging.getLogger(__name__)


class TanatException(Exception):
    """
    Base class for all custom exceptions raised by this module.
    """


class TanatOSError(TanatException):
    """
    OSErrors.
    """


class TanatValueError(TanatException):
    """
    ValueErrors.
    """


class TanatDataLoadError(TanatException):
    """Exception raised when loading Tanat embedded datasets fails."""


class ExpectedExceptionContext:
    """
    Context manager to convert expected exceptions to subclasses of
    TanatException.
    """

    # Predefined map of commonly expected exceptions to custom exception
    # subclasses.
    EXCEPTION_MAP = {
        OSError: TanatOSError,
        ValueError: TanatValueError,
        yaml.YAMLError: TanatValueError,
        pd.errors.EmptyDataError: TanatDataLoadError,
        FileNotFoundError: TanatDataLoadError,
    }

    def __init__(self, *expected, error_msg=None):
        """
        Args:
            *expected:
                The expected exceptions to transform into custom exceptions.
                These must be exception classes that are already in
                EXCEPTION_MAP.

            error_msg:
                An error message to prepend to the caught exception when
                instantiating the custom exception. It should provide context
                for the exception when it is displayed to the user.
        """
        expected = tuple(expected)
        for exception in expected:
            if exception not in self.EXCEPTION_MAP:
                raise ValueError(
                    f"{exception} is not mapped to any subclass of {TanatException}"
                )
        self._expected = expected
        self.error_msg = error_msg

    def __enter__(self):
        return self._expected

    def __exit__(self, typ, value, traceback):
        if typ is not None:
            for exp_type in self._expected:
                if issubclass(typ, exp_type):
                    if self.error_msg:
                        arg = f"{self.error_msg}: {value}"
                    else:
                        arg = value
                    raise self.EXCEPTION_MAP[exp_type](arg) from value
