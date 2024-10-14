import pytest

from syntask.settings import SYNTASK_ASYNC_FETCH_STATE_RESULT, temporary_settings
from syntask.testing.utilities import syntask_test_harness


@pytest.fixture(scope="session", autouse=True)
def syntask_db():
    """
    Sets up test harness for temporary DB during test runs.
    """
    with syntask_test_harness():
        yield


@pytest.fixture(autouse=True)
def fetch_state_result():
    with temporary_settings(updates={SYNTASK_ASYNC_FETCH_STATE_RESULT: True}):
        yield
