#!/usr/bin/env python3
"""
Utilities for criterion validation and resolution.
"""

from pypassist.mixin.registrable.exceptions import UnregisteredTypeError

from .base.enum import CriterionLevel
from .base.exception import InvalidCriterionError
from .base.settings import Criterion


def validate_criterion_params(criterion, level=None, criterion_type=None):
    """
    Validate criterion parameters and extract criterion_type if needed.

    Args:
        criterion (Union[Criterion, dict]): The criterion.
        level (str or CriterionLevel, optional): The criterion level.
        criterion_type (str, optional): The criterion type.

    Returns:
        str: The validated or extracted criterion_type.

    Raises:
        InvalidCriterionError: If validation fails.
    """
    if isinstance(criterion, dict):
        if criterion_type is None:
            raise InvalidCriterionError(
                "criterion_type must be provided if criterion is a dictionary."
            )
        if level is None:
            raise InvalidCriterionError(
                "level must be provided if criterion is a dictionary."
            )
    elif isinstance(criterion, Criterion):
        if criterion_type is None:
            # Extract criterion_type from criterion if not provided
            criterion_type = extract_criterion_type(criterion)
    elif not isinstance(criterion, Criterion) and not isinstance(criterion, dict):
        raise InvalidCriterionError(
            f"criterion must be a Criterion object or a dictionary. Got: {type(criterion)}"
        )

    return criterion_type


def resolve_criterion_level(criterion, provided_level=None, max_level=None):
    """
    Unified function to determine the correct CriterionLevel for any context.

    Args:
        criterion (Union[Criterion, dict]): The criterion.
        provided_level (str or CriterionLevel, optional): The provided criterion level.
        max_level (CriterionLevel, optional): The maximum level to consider.
            If None, defaults to SEQUENCE level for backward compatibility.

    Returns:
        CriterionLevel: The resolved criterion level.

    Raises:
        ValueError: If level must be provided but isn't (for trajectory context).
        InvalidCriterionError: If the provided level is incompatible with the criterion.
    """
    # Default compatibility levels based on max_level
    if max_level is None:
        # Backward compatibility: default to sequence context
        compatibility_levels = [CriterionLevel.SEQUENCE, CriterionLevel.ENTITY]
    else:
        # Full hierarchy up to max_level
        all_levels = [
            CriterionLevel.ENTITY,
            CriterionLevel.SEQUENCE,
            CriterionLevel.TRAJECTORY,
        ]
        compatibility_levels = [level for level in all_levels if level <= max_level]

    # Override with criterion-specific compatibility if available
    if isinstance(criterion, Criterion):
        compatibility_levels = criterion.get_compatibility_levels(max_level=max_level)

    # Check if level must be provided
    if len(compatibility_levels) > 1 and provided_level is None:
        # Use ValueError for trajectory context (backward compatibility)
        if max_level == CriterionLevel.TRAJECTORY:
            raise ValueError(
                "level must be provided if criterion is applicable at multiple levels."
            )

        raise InvalidCriterionError(
            "level must be provided if criterion is applicable at multiple levels."
        )

    # Convert string to enum if needed
    if isinstance(provided_level, str):
        provided_level = CriterionLevel.from_str(provided_level)

    # Validate compatibility
    if provided_level is not None and provided_level not in compatibility_levels:
        raise InvalidCriterionError(
            f"Level '{provided_level}' is not compatible with {criterion.__class__.__name__}. "
            f"Compatible levels: {compatibility_levels}"
        )

    # Return resolved level
    if provided_level is None:
        provided_level = compatibility_levels[0]

    return provided_level


# Backward compatibility alias
def resolve_trajectory_level(criterion, provided_level):
    """
    Backward compatibility wrapper for trajectory operations.

    Args:
        criterion (Union[Criterion, dict]): The criterion.
        provided_level (str or CriterionLevel, optional): The provided criterion level.

    Returns:
        CriterionLevel: The resolved criterion level.
    """
    return resolve_criterion_level(
        criterion, provided_level, max_level=CriterionLevel.TRAJECTORY
    )


def resolve_and_init_criterion(
    criterion, level=None, criterion_type=None, max_level=None
):
    """
    Ultimate function that validates, resolves level, and initializes criterion in one call.

    This function combines validate_criterion_params, resolve_criterion_level,
    and criterion initialization to eliminate code duplication across all methods.

    Args:
        criterion (Union[Criterion, dict]): The criterion to process.
        level (str or CriterionLevel, optional): The criterion level.
        criterion_type (str, optional): The criterion type.
        max_level (CriterionLevel, optional): The maximum level to consider.
            If None, defaults to SEQUENCE level context.

    Returns:
        tuple: (criterion_instance, resolved_level)
            - criterion_instance: Initialized criterion object ready to use
            - resolved_level: The resolved CriterionLevel

    Raises:
        InvalidCriterionError: If validation or resolution fails.
    """
    # Step 1: Validate and extract criterion_type
    criterion_type = validate_criterion_params(criterion, level, criterion_type)

    # Step 2: Resolve the appropriate level using unified function
    resolved_level = resolve_criterion_level(criterion, level, max_level)

    # Step 3: Get the registry class and initialize criterion
    criterion_base_cls = resolved_level.get_registry_cls()

    try:
        criterion_instance = criterion_base_cls.init(criterion, criterion_type)
    except UnregisteredTypeError as err:
        raise InvalidCriterionError(
            f"Criterion provided is not compatible for {resolved_level}"
        ) from err

    return criterion_instance, resolved_level


def extract_criterion_type(criterion):
    """
    Extract criterion type from criterion object.

    Args:
        criterion (Criterion): The criterion object.

    Returns:
        str: The criterion type.

    Raises:
        ValueError: If criterion_type cannot be extracted.
    """
    criterion_type = getattr(criterion, "_REGISTER_NAME", None)
    if criterion_type is None:
        raise ValueError(
            "Invalid settings: missing '_REGISTER_NAME' attribute. "
            "Use a valid settings class or specify criterion_type."
        )
    return criterion_type
