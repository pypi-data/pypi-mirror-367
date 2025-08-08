#!/usr/bin/env python3
"""
Direct zero setter.
"""

import logging

from ...setter import ZeroSetter
from .settings import DirectZeroSetterSettings

LOGGER = logging.getLogger(__name__)


class DirectZeroSetter(ZeroSetter, register_name="direct"):
    """
    Set sequence(s) or trajectory(s) t_zero from direct input.
    Handles both single objects and pools.
    """

    SETTINGS_DATACLASS = DirectZeroSetterSettings

    def assign(self, target, **kwargs):
        """
        Assign t_zero from direct input.

        Args:
            target: Single sequence/trajectory or pool object
            **kwargs: Additional keyword arguments to override settings

        Returns:
            The same object with t_zero assigned
        """
        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            input_value = self.settings.value

            if not isinstance(input_value, dict):
                target._t_zero = input_value
                return self._clear_cache_and_return(target)

            target = self._assign_from_dict(target, input_value)
            return self._clear_cache_and_return(target)

    def _assign_from_dict(self, target, input_value):
        """
        Helper method to assign t_zero from a dictionary input.

        Args:
            target: Target sequence/trajectory or pool object
            input_value: Dictionary with ID -> date mappings

        Returns:
            Updated target object
        """
        target_ids = self._get_target_ids(target)
        valid_input_value = self._filter_valid_ids(input_value, target_ids)

        if not valid_input_value:
            LOGGER.warning(
                "t_zero: No input ID(s) matched target ID(s). "
                "t_zero will be set to None."
            )
            target._t_zero = None
            return target

        final_value = self._extract_final_value(valid_input_value)
        target._t_zero = final_value
        return target

    def _filter_valid_ids(self, input_value, target_ids):
        """
        Filter input dictionary to only include valid target IDs.

        Args:
            input_value: Dictionary with ID -> date mappings
            target_ids: Valid target IDs

        Returns:
            Filtered dictionary containing only valid IDs
        """
        input_ids = set(input_value.keys())
        valid_target_ids = set(target_ids)

        invalid_ids = input_ids - valid_target_ids
        if invalid_ids:
            LOGGER.warning(
                "t_zero: Input ID(s) do not match target ID(s). %s will be ignored.",
                invalid_ids,
            )

        return {k: v for k, v in input_value.items() if k in valid_target_ids}

    def _extract_final_value(self, valid_input_value):
        """
        Extract the final value to assign from the valid input dictionary.

        Args:
            valid_input_value: Dictionary with valid ID -> date mappings

        Returns:
            Single value if dictionary has one item, otherwise the full dictionary
        """
        if len(valid_input_value) == 1:
            return next(iter(valid_input_value.values()))
        return valid_input_value
