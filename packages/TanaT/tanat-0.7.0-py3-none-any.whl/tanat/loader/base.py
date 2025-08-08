#!/usr/bin/env python3
"""
Loader base class
"""

from abc import ABC, abstractmethod

from pypassist.mixin.cachable import Cachable
from pypassist.mixin.settings import SettingsMixin
from pypassist.mixin.registrable import Registrable, UnregisteredTypeError
from pydantic_core import core_schema

from .exception import UnregisteredLoaderTypeError


class Loader(
    ABC,
    Registrable,
    Cachable,
    SettingsMixin,
):
    """Base class for all loaders"""

    _REGISTER = {}
    _TYPE_SUBMODULE = "type"

    def __init__(self, settings):
        """
        Initialize the loader with the given settings.

        Args:
            settings: Configuration settings for the loader.

        Raises:
            ValueError: If the settings type is invalid.
        """
        SettingsMixin.__init__(self, settings)
        Cachable.__init__(self)

    def load(self):
        """
        Load data using the settings provided at initialization.

        Returns:
            The loaded data.
        """
        return self._load_impl(self.settings)

    @abstractmethod
    def _load_impl(self, settings):
        """
        Implementation of the data loading logic.

        Args:
            settings: Configuration settings for the loader.
            Mostly there for caching invalidation

        Returns:
            The loaded data.
        """

    def __call__(self):
        """
        Allow the loader to be called as a function.

        Returns:
            The loaded data.
        """
        return self.load()

    @classmethod
    def get_loader(cls, ltype, settings=None):
        """
        Retrieve and instantiate a Loader.

        Args:
            ltype: Type of loader to use, resolved via type registry.
            settings: Loader-specific settings dictionary or dataclass.

        Returns:
            An instance of the Loader configured
            with the provided settings.

        Raises:
            UnregisteredLoaderTypeError: If the loader type is not registered.
        """
        try:
            loader_cls = cls.get_registered(ltype)
            return loader_cls(settings=settings)
        except UnregisteredTypeError as err:
            raise UnregisteredLoaderTypeError(
                f"Unknown loader type: '{ltype}'."
                f"Available loaders: {cls.list_registered()}"
            ) from err

    def refresh(self):
        """
        Reload the data.

        Returns:
            The reloaded data.
        """
        self.clear_cache()
        return self.load()

    def __get_pydantic_core_schema__(self, handler):  # pylint: disable=unused-argument
        """Pydantic schema override."""
        return core_schema.any_schema()
