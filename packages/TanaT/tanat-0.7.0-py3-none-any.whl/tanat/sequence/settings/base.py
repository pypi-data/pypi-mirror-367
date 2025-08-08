#!/usr/bin/env python3
"""
Base settings for sequence objects.
"""

import logging
import dataclasses
from abc import ABC

from pypassist.fallback.typing import List
from pypassist.utils.convert import ensure_list

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class BaseSequenceSettings(ABC):
    """
    Base configuration for sequence objects.

    Provides core settings for sequence identification and entity feature
    management across all sequence types. Serves as foundation for
    specialized sequence configurations.

    Attributes:
        id_column (str): Column name containing sequence identifiers.
        entity_features (List[str]): Column names for entity features
            (events, states, intervals, etc.).
    """

    id_column: str
    entity_features: List[str]

    def get_sequence_data_columns(self, standardize=False, entity_features=None):
        """
        Get a list of columns representing sequence data (i.e. temporal and data columns).
        """
        entity_features = self.validate_and_filter_entity_features(entity_features)
        # pylint: disable=no-member
        return [
            # self.id_column,
            *self.temporal_columns(standardize),
            *entity_features,
        ]

    def get_valid_columns(self):
        """
        Get a list of valid column names, unpacking lists.
        """
        excluded_fields = [
            "anchor",
            "static_features",
        ]
        column_names = []
        for field in dataclasses.fields(self):
            if field.name in excluded_fields:
                continue
            field_value = getattr(self, field.name)
            if isinstance(field_value, list):
                column_names.extend(field_value)
            else:
                column_names.append(field_value)
        return column_names

    def validate_and_filter_entity_features(
        self,
        subset_entity_features,
    ):
        """
        Validate and filter entity features with warnings for invalid ones.

        Args:
            subset_entity_features: Requested features (str, list, or None)

        Returns:
            List[str]: Filtered list of valid features
        Raises:
            ValueError: If no valid features remain after filtering
            TypeError: If entity_features has invalid type
        """
        default_features = self.entity_features
        if subset_entity_features is None:
            return default_features

        subset_entity_features = ensure_list(subset_entity_features)
        valid_features = []
        invalid_features = []
        for feature in subset_entity_features:
            if feature not in default_features:
                invalid_features.append(feature)
                continue

            valid_features.append(feature)

        if invalid_features:
            LOGGER.warning(
                "Invalid features %s provided. Will be ignored.\nAllowed features: %s.",
                invalid_features,
                default_features,
            )

        if not valid_features:
            raise ValueError(
                "No valid entity features provided.\n"
                f"Allowed features are: {default_features}. "
            )

        return valid_features
