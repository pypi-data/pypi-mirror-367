#!/usr/bin/env python3
"""
Sequence criterion configuration.
"""

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators import registry
from pypassist.dataclass.decorators.exportable.decorator import exportable

from .base.applier import SequenceCriterionApplier
from ..config import CriterionConfig


@registry(base_cls=SequenceCriterionApplier, register_name_attr="criterion_type")
@exportable(strategy="registry")
@dataclass
class SequenceCriterionConfig(CriterionConfig):
    """
    Sequence criterion configuration.

    Attributes:
        criterion_type: Type of criterion to use, resolved via type registry.
        settings: Criterion-specific settings dictionary.

    Example:
        ```yaml
        criterion_type: "query"
        settings:
            query: "event = 'hospitalization'"
        ```
    """
