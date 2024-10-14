import asyncio
import logging
import sys

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


@pytest.fixture(scope="session")
def event_loop(request):
    """
    Redefine the event loop to support session/module-scoped fixtures;
    see https://github.com/pytest-dev/pytest-asyncio/issues/68
    When running on Windows we need to use a non-default loop for subprocess support.
    """
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    policy = asyncio.get_event_loop_policy()

    loop = policy.new_event_loop()

    # configure asyncio logging to capture long running tasks
    asyncio_logger = logging.getLogger("asyncio")
    asyncio_logger.setLevel("WARNING")
    asyncio_logger.addHandler(logging.StreamHandler())
    loop.set_debug(True)
    loop.slow_callback_duration = 0.25

    try:
        yield loop
    finally:
        loop.close()

    # Workaround for failures in pytest_asyncio 0.17;
    # see https://github.com/pytest-dev/pytest-asyncio/issues/257
    policy.set_event_loop(loop)


@pytest.fixture(autouse=True)
def fetch_state_result():
    with temporary_settings(updates={SYNTASK_ASYNC_FETCH_STATE_RESULT: True}):
        yield
