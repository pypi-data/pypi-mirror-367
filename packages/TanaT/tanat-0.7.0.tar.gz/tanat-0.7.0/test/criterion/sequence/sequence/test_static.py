#!/usr/bin/env python3
"""
Test static criterion applied to a single sequence.
"""

import pytest

from tanat.criterion.mixin.static.settings import StaticCriterion
from tanat.criterion.base.exception import InvalidCriterionError


class TestStaticCriterion:
    """
    Test the static match method applied to individual sequence.
    """

    @pytest.mark.parametrize(
        "pool_type,sequence_id",
        [
            ("event", 1),
            ("state", 1),
            ("interval", 1),
        ],
    )
    def test_static_match_object_returns_true(
        self, sequence_pools, pool_type, sequence_id
    ):
        """
        Match should return True with a valid StaticCriterion object.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]

        valid_criterion = StaticCriterion(query="age > 65")
        assert sequence.match(valid_criterion)

    @pytest.mark.parametrize(
        "pool_type,sequence_id",
        [
            ("event", 1),
            ("state", 1),
            ("interval", 1),
        ],
    )
    def test_static_match_dict_returns_true(
        self, sequence_pools, pool_type, sequence_id
    ):
        """
        Match should return True with a valid static criterion dict.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]

        criterion_dict = {"query": "age > 65"}
        assert sequence.match(criterion_dict, criterion_type="static")

    @pytest.mark.parametrize(
        "pool_type,sequence_id",
        [
            ("event", 1),
            ("state", 1),
            ("interval", 1),
        ],
    )
    def test_static_match_object_returns_false(
        self, sequence_pools, pool_type, sequence_id
    ):
        """
        Match should return False for an invalid StaticCriterion object.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]

        invalid_criterion = StaticCriterion(query="age < 0")
        assert not sequence.match(invalid_criterion)

    @pytest.mark.parametrize(
        "pool_type,sequence_id",
        [
            ("event", 1),
            ("state", 1),
            ("interval", 1),
        ],
    )
    def test_static_match_dict_returns_false(
        self, sequence_pools, pool_type, sequence_id
    ):
        """
        Match should return False for an invalid static criterion dict.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]

        criterion_dict = {"query": "age < 0"}
        assert not sequence.match(criterion_dict, criterion_type="static")

    @pytest.mark.parametrize(
        "pool_type,sequence_id",
        [
            ("event", 1),
            ("state", 1),
            ("interval", 1),
        ],
    )
    def test_static_match_object_with_valid_override(
        self, sequence_pools, pool_type, sequence_id
    ):
        """
        Match should return True when invalid StaticCriterion is overridden by valid kwargs.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]

        invalid_criterion = StaticCriterion(query="age < 0")
        assert not sequence.match(invalid_criterion)

        # Override to force valid match
        result = sequence.match(invalid_criterion, query="age > 65")
        assert result

    @pytest.mark.parametrize(
        "pool_type,sequence_id",
        [
            ("event", 1),
            ("state", 1),
            ("interval", 1),
        ],
    )
    def test_static_match_dict_with_valid_override(
        self, sequence_pools, pool_type, sequence_id
    ):
        """
        Match should return True when invalid dict criterion is overridden by valid kwargs.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]

        criterion_dict = {"query": "age < 0"}
        assert not sequence.match(criterion_dict, criterion_type="static")

        # Override via kwargs
        result = sequence.match(
            criterion_dict, criterion_type="static", query="age > 65"
        )
        assert result

    @pytest.mark.parametrize(
        "pool_type,sequence_id",
        [
            ("event", 4),
            ("interval", 1),
        ],
    )
    def test_filter_entities_raises_error(self, sequence_pools, pool_type, sequence_id):
        """
        Filter entities should raise an error because static criterion cannot be applied at entity level.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]
        criterion_kwargs = {"query": "age > 65"}
        criterion = StaticCriterion(**criterion_kwargs)

        with pytest.raises(InvalidCriterionError):
            sequence.filter(criterion)

        ## -- from dict
        with pytest.raises(InvalidCriterionError):
            sequence.filter(criterion_kwargs, criterion_type="static")

    def test_filter_entities_on_state_sequence_raises_not_implemented_error(
        self, sequence_pools
    ):
        """
        Filter entities should raise a NotImplementedError.
        """
        state_pool = sequence_pools["state"]
        sequence = state_pool[1]
        criterion_kwargs = {"query": "age > 65"}
        criterion = StaticCriterion(**criterion_kwargs)

        with pytest.raises(NotImplementedError):
            sequence.filter(criterion)

        ## -- from dict
        with pytest.raises(NotImplementedError):
            sequence.filter(criterion_kwargs, criterion_type="static")
