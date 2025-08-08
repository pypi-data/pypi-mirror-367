"""Tests for ForEach class registry integration."""

from unittest.mock import patch

import pytest

from doteval.core import ForEach, foreach
from doteval.datasets import Dataset, DatasetRegistry
from doteval.evaluators import exact_match
from doteval.models import Result


class MockDataset(Dataset):
    """Simple test dataset."""

    name = "test_dataset"
    splits = ["train", "test"]
    columns = ["question", "answer"]

    def __init__(self, split, **kwargs):
        self.split = split
        self.limit = kwargs.get("limit", 2)
        self.num_rows = min(self.limit, 2)

    def __iter__(self):
        data = [("What is 2+2?", "4"), ("What is 3+3?", "6")]

        yield from data[: self.limit]


@pytest.fixture
def test_registry():
    """Provide clean registry with test data."""
    registry = DatasetRegistry()
    registry.register(MockDataset)
    return registry


def test_foreach_getattr_creates_decorator(test_registry):
    """Test that foreach.dataset_name() returns a decorator."""
    with patch("doteval.core._registry", test_registry):
        decorator = foreach.test_dataset("test")
        assert callable(decorator)


def test_foreach_getattr_decorates_function(test_registry):
    """Test decorator properly wraps functions."""
    with patch("doteval.core._registry", test_registry):
        decorator = foreach.test_dataset("test")

        @decorator
        def eval_fn(question, answer):
            return True

        assert callable(eval_fn)
        assert hasattr(eval_fn, "__wrapped__")


@pytest.mark.parametrize(
    "split,kwargs",
    [
        ("test", {}),
        ("train", {"limit": 1}),
    ],
)
def test_foreach_getattr_with_parameters(test_registry, split, kwargs):
    """Test foreach.dataset_name with different parameters."""
    with patch("doteval.core._registry", test_registry):
        decorator = foreach.test_dataset(split, **kwargs)

        @decorator
        def eval_fn(question, answer):
            return True

        assert callable(eval_fn)


def test_foreach_getattr_preserves_function_metadata(test_registry):
    """Test decorator preserves function name and docstring."""
    with patch("doteval.core._registry", test_registry):
        decorator = foreach.test_dataset("test")

        @decorator
        def my_evaluation(question, answer):
            """My test evaluation."""
            return True

        assert my_evaluation.__name__ == "my_evaluation"
        assert my_evaluation.__doc__ == "My test evaluation."


def test_foreach_getattr_nonexistent_dataset():
    """Test foreach.nonexistent raises appropriate error."""
    with pytest.raises(ValueError, match="Dataset 'nonexistent' not found"):
        foreach.nonexistent("test")


def test_foreach_getattr_async_function(test_registry):
    """Test foreach works with async functions."""
    with patch("doteval.core._registry", test_registry):
        decorator = foreach.test_dataset("test")

        @decorator
        async def async_eval(question, answer):
            return True

        import asyncio

        assert asyncio.iscoroutinefunction(async_eval.__wrapped__)


def test_foreach_different_instances():
    """Test ForEach instances behave consistently."""
    custom_foreach = ForEach()

    # Both should access same global registry
    try:
        decorator1 = foreach.gsm8k("test")
        decorator2 = custom_foreach.gsm8k("test")

        assert callable(decorator1)
        assert callable(decorator2)
    except ValueError:
        # Expected if gsm8k not available in test environment
        pass


def test_foreach_getattr_with_real_gsm8k():
    """Test foreach.gsm8k works with real registered dataset."""
    try:
        # GSM8K might be available via plugin
        decorator = foreach.gsm8k("test")

        @decorator
        def eval_gsm8k(question, answer):
            return {"exact_match": True}

        assert callable(eval_gsm8k)
        assert hasattr(eval_gsm8k, "__wrapped__")
    except ValueError:
        # Expected if doteval-datasets is not installed
        pytest.skip("GSM8K dataset not available (install doteval-datasets)")


def test_foreach_getattr_without_split_argument():
    """Test foreach.dataset_name() works when split is omitted (split=None)."""

    class NoSplitDataset(Dataset):
        name = "no_split_dataset"
        splits = []
        columns = ["x", "y"]

        def __init__(self, **kwargs):
            self.num_rows = 1

        def __iter__(self):
            yield (1, 2)

    registry = DatasetRegistry()
    registry.register(NoSplitDataset)

    with patch("doteval.core._registry", registry):
        decorator = foreach.no_split_dataset()

        @decorator
        def eval_fn(x, y):
            return Result(exact_match(x, y), prompt="")

        # Should be callable (actual execution would need session context)
        assert callable(eval_fn)
        # Verify it's set up for pytest integration
        assert hasattr(eval_fn, "__wrapped__")
