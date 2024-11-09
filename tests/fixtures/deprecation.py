"""
Fixture to ignore our own deprecation warnings.

Deprecations should be specifically tested to ensure they are emitted as expected.
"""

import warnings

import pytest

from syntask._internal.compatibility.deprecated import SyntaskDeprecationWarning


@pytest.fixture(autouse=True)
def ignore_syntask_deprecation_warnings():
    """
    Ignore deprecation warnings from the agent module to avoid
    test failures.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=SyntaskDeprecationWarning)
        yield
