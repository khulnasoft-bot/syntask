import pytest

from syntask.testing.utilities import syntask_test_harness


@pytest.fixture(scope="session", autouse=True)
def syntask_db():
    """
    Sets up test harness for temporary DB during test runs.
    """
    with syntask_test_harness():
        yield
