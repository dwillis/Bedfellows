"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration between tests."""
    import logging

    # Clear all handlers
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    # Reset level
    root.setLevel(logging.WARNING)
