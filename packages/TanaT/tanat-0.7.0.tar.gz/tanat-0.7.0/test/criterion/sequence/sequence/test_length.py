#!/usr/bin/env python3
"""
Test length criterion applied to a single sequence.
"""

import pytest

from tanat.criterion.sequence.type.length.settings import LengthCriterion
from tanat.criterion.base.exception import InvalidCriterionError


class TestLengthCriterion:
    """
    Test the match method applied to individual sequence using length criterion.
    """

    @pytest.mark.parametrize(
        "pool_type,sequence_id,criterion_kwargs",
        [
            ("event", 2, {"gt": 3}),
            ("state", 3, {"le": 4}),
            ("interval", 2, {"ge": 2, "lt": 10}),
        ],
    )
    def test_match_returns_true_on_valid_sequence(
        self, sequence_pools, pool_type, sequence_id, criterion_kwargs
    ):
        """
        Should return True when a sequence satisfies the length criterion.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]

        criterion = LengthCriterion(**criterion_kwargs)

        assert sequence.match(criterion) is True

    @pytest.mark.parametrize(
        "pool_type,sequence_id, criterion_kwargs",
        [
            ("event", 3, {"gt": 50}),
            ("state", 1, {"lt": 1}),
            ("interval", 4, {"ge": 100}),
        ],
    )
    def test_match_returns_false_on_invalid_sequence(
        self, sequence_pools, pool_type, sequence_id, criterion_kwargs
    ):
        """
        Should return False when a sequence does NOT satisfy the length criterion.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]

        criterion = LengthCriterion(**criterion_kwargs)

        assert sequence.match(criterion) is False

    @pytest.mark.parametrize(
        "pool_type,sequence_id,aberrant_ge,override_kwargs",
        [
            ("event", 4, 600, {"ge": 10}),
            ("state", 3, 600, {"ge": 3}),
            ("interval", 1, 600, {"ge": 2, "lt": 15}),
        ],
    )
    def test_match_via_dict_input_with_override(
        self, sequence_pools, pool_type, sequence_id, aberrant_ge, override_kwargs
    ):
        """
        Test if kwargs can override criterion parameters.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]
        criterion = LengthCriterion(ge=aberrant_ge)

        assert not sequence.match(criterion)
        assert sequence.match(criterion, **override_kwargs)

    @pytest.mark.parametrize(
        "pool_type,sequence_id,criterion_kwargs",
        [
            ("event", 4, {"ge": 2, "lt": 15}),
            ("interval", 1, {"ge": 2, "lt": 15}),
        ],
    )
    def test_filter_entities_raises_error(
        self, sequence_pools, pool_type, sequence_id, criterion_kwargs
    ):
        """
        Filter entities should raise an error because length criterion cannot be applied at entity level.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]
        criterion = LengthCriterion(**criterion_kwargs)

        with pytest.raises(InvalidCriterionError):
            sequence.filter(criterion)

        ## -- from dict
        with pytest.raises(InvalidCriterionError):
            sequence.filter(criterion, criterion_type="length")

    def test_filter_entities_on_state_sequence_raises_not_implemented_error(
        self, sequence_pools
    ):
        """
        Filter entities should raise a NotImplementedError.
        """
        state_pool = sequence_pools["state"]
        sequence = state_pool[1]
        criterion_kwargs = {"gt": 5}
        criterion = LengthCriterion(**criterion_kwargs)

        with pytest.raises(NotImplementedError):
            sequence.filter(criterion)

        ## -- from dict
        with pytest.raises(NotImplementedError):
            sequence.filter(criterion_kwargs, criterion_type="length")
