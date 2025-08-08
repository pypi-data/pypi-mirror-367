#!/usr/bin/env python3
"""
Utility functions for sequence settings.
"""


def _create_child_settings(base_settings, **overrides):
    """
    Create child settings with specified overrides.

    Args:
        base_settings: Base settings instance to copy from.
        **overrides: Attributes to override in new settings.

    Returns:
        New settings instance with overrides applied.
    """
    settings_dict = {}
    for field_name in base_settings.__dataclass_fields__:
        settings_dict[field_name] = getattr(base_settings, field_name)
    settings_dict.update(overrides)
    return base_settings.__class__(**settings_dict)
