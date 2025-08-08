#!/usr/bin/env python3
"""
Loader exceptions.
"""

from pypassist.mixin.registrable.exceptions import UnregisteredTypeError

from ..exception import TanatException


class LoaderException(TanatException):
    """
    Base class for exceptions raised by loaders.
    """


class UnregisteredLoaderTypeError(UnregisteredTypeError, LoaderException):
    """
    Exception raised when a loader type is not registered.
    """
