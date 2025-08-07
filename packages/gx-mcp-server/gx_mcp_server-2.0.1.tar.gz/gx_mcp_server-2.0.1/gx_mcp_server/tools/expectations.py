# gx_mcp_server/tools/expectations.py
"""
MCP tools for managing Great Expectations suites and expectations.
"""

import threading
from typing import TYPE_CHECKING, Any, Dict

import great_expectations as gx
from great_expectations.core import ExpectationSuite
from great_expectations.exceptions import DataContextError

from gx_mcp_server.logging import logger
from gx_mcp_server.core import schema
from gx_mcp_server.core.context import get_shared_context
from importlib.metadata import version


API_VERSION = version("gx-mcp-server")


def get_version() -> dict:
    """Return the API version for MCP server."""
    return {"version": API_VERSION}


if TYPE_CHECKING:
    from fastmcp import FastMCP

_lock = threading.Lock()


def create_suite(
    suite_name: str,
    dataset_handle: str,
    profiler: bool = False,
) -> schema.SuiteHandle:
    """Create a named ExpectationSuite, optionally profiled from a dataset.

    Args:
        suite_name: Name for the new expectation suite
        dataset_handle: Handle to dataset (currently unused, for future profiling)
        profiler: Whether to auto-generate expectations via profiling (deprecated)

    Returns:
        SuiteHandle: Handle to the created suite

    Note:
        Profiler functionality is deprecated in Great Expectations 1.5+.
        Create empty suites and add expectations manually using add_expectation.

    Deprecated:
        The 'profiler' argument is deprecated and will be removed in a future release.
    """
    import warnings

    logger.info("Creating suite '%s' (profiler=%s)", suite_name, profiler)
    context = get_shared_context()

    with _lock:
        # Initialize an empty suite
        suite = ExpectationSuite(suite_name)
        context.suites.add(suite)
    logger.info("Suite '%s' registered in context", suite_name)

    if profiler:
        warnings.warn(
            "The 'profiler' argument is deprecated and will be removed in a future release.",
            DeprecationWarning,
        )
        # NOTE: Profiler functionality has been deprecated in Great Expectations 1.5+
        # For now, we'll log a warning and create an empty suite
        logger.warning(
            "Profiler functionality is deprecated in Great Expectations 1.5+. "
            "Creating empty suite instead. Please add expectations manually."
        )

    return schema.SuiteHandle(suite_name=suite_name)


def add_expectation(
    suite_name: str,
    expectation_type: str,
    kwargs: Dict[str, Any],
) -> schema.ToolResponse:
    """Add a single expectation to an existing suite (or create it).

    Args:
        suite_name: Name of the expectation suite
        expectation_type: Type of expectation (e.g., "expect_column_values_to_be_in_set")
        kwargs: Parameters for the expectation (e.g., {"column": "status", "value_set": ["active", "inactive"]})

    Returns:
        ToolResponse: Success/failure status and message

    Examples:
        - Column values in set: add_expectation("my_suite", "expect_column_values_to_be_in_set", {"column": "status", "value_set": ["A", "B"]})
        - Column not null: add_expectation("my_suite", "expect_column_values_to_not_be_null", {"column": "id"})
        - Table row count: add_expectation("my_suite", "expect_table_row_count_to_be_between", {"min_value": 1, "max_value": 1000})
    """
    logger.info(
        "Adding expectation '%s' to suite '%s' with keys=%s",
        expectation_type,
        suite_name,
        list(kwargs.keys()),
    )
    context = get_shared_context()
    with _lock:
        try:
            try:
                suite = context.suites.get(name=suite_name)
            except DataContextError:
                logger.info("Suite '%s' not found, creating a new one.", suite_name)
                suite = ExpectationSuite(suite_name)

            # Instantiate the expectation and add it
            impl = gx.expectations.registry.get_expectation_impl(expectation_type)
            expectation = impl(**kwargs)
            suite.add_expectation(expectation)
            context.suites.add_or_update(suite)
            logger.info(
                "Expectation '%s' added to suite '%s'",
                expectation_type,
                suite_name,
            )
            return schema.ToolResponse(success=True, message="Expectation added")
        except Exception as e:
            logger.error("Failed to add expectation: %s", str(e))
            return schema.ToolResponse(
                success=False, message=f"Expectation addition failed: {str(e)}"
            )


def register(mcp_instance: "FastMCP") -> None:
    """Register expectation tools with the MCP instance."""
    mcp_instance.tool()(create_suite)
    mcp_instance.tool()(add_expectation)
    mcp_instance.tool()(get_version)
