"""Pytest plugin for doteval - LLM evaluation framework integration.

This module provides seamless integration between doteval's evaluation system and pytest's
test discovery and execution framework. It allows evaluation functions decorated with
@foreach to be collected and executed as pytest tests.

The plugin uses a unified collection system where ALL doteval functions are collected
during pytest's collection phase and executed at session end using appropriate runners:

1. **Collection Phase** (pytest_collection_modifyitems):
   - All functions with @foreach decorators are marked with 'doteval' marker
   - All doteval items are collected into config._doteval_items for deferred execution

2. **Test Execution Phase** (pytest_runtest_call):
   - All doteval functions are SKIPPED during normal test execution
   - Fixture values are captured and stored for later use (when pytest's fixture system is active)
   - This ensures doteval functions don't interfere with normal pytest test flow

3. **Session End** (pytest_sessionfinish):
   - Collected doteval items are executed using appropriate runners:
     * SequentialRunner: For sync functions and async functions in non-concurrent mode
     * ConcurrentRunner: For async functions when --concurrent flag is used
   - Results are stored in config._evaluation_results for retrieval
"""

import asyncio
from typing import Optional, Union

import pytest
from pytest import Config, Function, Item, Metafunc, Parser, Session

# Import model provider discovery fixtures
from doteval.providers import model_providers

__all__ = ["model_providers"]


@pytest.hookimpl
def pytest_addoption(parser: Parser) -> None:
    """Add command line options that are specific to doteval.

    This hook registers custom CLI options that doteval users can pass to pytest:
    - --samples: Limit the number of dataset samples to evaluate
    - --experiment: Name the experiment for result storage
    - --concurrent: Number of concurrent evaluations to run (similar to pytest-xdist syntax)

    Args:
        parser: Pytest's argument parser for adding custom command line options.
                This is a pytest.config.argparsing.Parser instance.

    Note:
        This is a pytest hook implementation that gets called during pytest initialization.
        The parser parameter is automatically provided by pytest.
    """
    parser.addoption(
        "--samples", type=int, help="Maximum number of dataset samples to evaluate"
    )
    parser.addoption("--experiment", type=str, help="Name of the experiment")
    parser.addoption(
        "-C",
        "--concurrent",
        action="store_true",
        default=False,
        help="Run async evaluations concurrently.",
    )


@pytest.hookimpl
def pytest_configure(config: Config) -> None:
    """Configure pytest for doteval integration.

    This hook extends pytest's collection patterns to include doteval evaluation files:
    - Collects files named `eval_*.py` (in addition to `test_*.py`)
    - Collects functions named `eval_*` (in addition to `test_*`)
    - Registers the 'doteval' marker for filtering evaluations vs tests
    - Initializes storage for evaluation results
    - Initializes storage for evaluation items

    Args:
        config: Pytest configuration object that holds command line options,
                ini-file values, and other configuration data.

    Note:
        This hook is called once per pytest session after command line options
        have been parsed but before test collection begins.
    """
    config.addinivalue_line("markers", "doteval: mark test as LLM evaluation")
    config.addinivalue_line("python_files", "eval_*.py")
    config.addinivalue_line("python_functions", "eval_*")
    config._evaluation_results = {}

    # Store evaluation items that pass marker filtering for deferred execution
    config._doteval_items = []


@pytest.hookimpl
def pytest_pyfunc_call(pyfuncitem: Function) -> bool | None:
    """Intercept function calls for doteval functions.

    This hook prevents pytest from trying to call doteval functions directly.

    Args:
        pyfuncitem: A pytest Function item representing a Python function to be executed.

    Returns:
        bool or None: True if we handled the call (for doteval functions),
                      None to let pytest handle it normally (for regular test functions).

    Note:
        Returning True indicates to pytest that we handled the call and it should
        not attempt to execute the function itself.
    """
    if pyfuncitem.get_closest_marker("doteval"):
        return True

    return None


@pytest.hookimpl
def pytest_generate_tests(metafunc: Metafunc) -> None:
    """Prevent fixture resolution errors for doteval functions.

    When pytest sees a function like `def eval_func(input, expected)`,
    it thinks 'input' and 'expected' are fixtures that need to be resolved. Pytest
    fixture resolution happens before our plugin is called.

    The solution: We pre-parametrize dataset column names with dummy values [None]
    to satisfy pytest's fixture resolution.

    Later, in pytest_runtest_call, our wrapper function will filter out these
    dummy values and only pass real fixture values to the evaluation.

    Args:
        metafunc: Pytest's Metafunc object that provides access to the test function
                  and allows parametrization of its arguments.

    Note:
        This hook is called for every test function during collection phase.
        Only doteval functions (those with _column_names attribute) are processed.
    """
    if hasattr(metafunc.function, "_column_names"):
        column_names = metafunc.function._column_names

        # Only parametrize dataset columns that pytest thinks are fixtures
        for column in column_names:
            if column in metafunc.fixturenames:
                metafunc.parametrize(column, [None])


@pytest.hookimpl
def pytest_runtest_call(item: Item) -> None | bool:
    """Skip doteval functions and store them for deferred execution.

    All doteval functions are executed at session end using the appropriate runner.

    Args:
        item: Pytest test item to be executed. For doteval functions, this contains
              the evaluation function and its associated metadata.

    Note:
        This is called for every test item during the execution phase.
        For doteval functions, we skip execution and store the item.
        For regular test functions, pytest continues with normal execution.
    """
    if item.get_closest_marker("doteval"):
        config = item.session.config
        config._doteval_items.append(item)
    return None


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session: Session, exitstatus: int | pytest.ExitCode) -> None:
    """Run all collected doteval items using appropriate runners.

    This handles both sequential and concurrent execution:
    - Sequential items are run one by one
    - Concurrent-eligible items are run together if concurrent mode is enabled

    Args:
        session: Pytest session object containing information about the test run.
        exitstatus: Exit status of the test session (0 for success, non-zero for failures).

    Note:
        The trylast=True ensures this runs after all other session finish hooks.
        This is where all doteval functions are actually executed using captured fixtures.
    """
    from doteval.runners import Runner

    config = session.config
    experiment_name = config.getoption("--experiment")
    samples = config.getoption("--samples")
    concurrent = config.getoption("concurrent", False)

    # Exit early if no doteval items were selected for execution
    # (e.g., when running -m "not doteval")
    if not getattr(config, "_doteval_items", []):
        return

    # Run all evaluations with the base runner
    async def run_all_evaluations() -> None:
        runner = Runner(
            experiment_name=experiment_name,
            samples=samples,
            concurrent=concurrent,
            results_dict=config._evaluation_results,
        )
        await runner.run_evaluations(config._doteval_items)

    # Execute
    asyncio.run(run_all_evaluations())
