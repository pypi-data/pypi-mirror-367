#!/usr/bin/env python3
"""
Trajectory criterion configuration.
"""

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators import registry
from pypassist.dataclass.decorators.exportable.decorator import exportable

from .base.applier import TrajectoryCriterionApplier
from ..config import CriterionConfig


@registry(base_cls=TrajectoryCriterionApplier, register_name_attr="criterion_type")
@exportable(strategy="registry")
@dataclass
class TrajectoryCriterionConfig(CriterionConfig):
    """
    Trajectory criterion configuration.

    Attributes:
        criterion_type: Type of criterion to use, resolved via type registry.
        settings: Criterion-specific settings dictionary.

    Example:
        ```yaml
        criterion_type: "static"
        settings:
            query: "age > 65"
        ```
    """
