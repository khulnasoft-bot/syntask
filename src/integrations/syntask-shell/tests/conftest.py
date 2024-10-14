import logging

import pytest

from syntask.testing.utilities import syntask_test_harness


@pytest.fixture(scope="session", autouse=True)
def syntask_db():
    """
    Sets up test harness for temporary DB during test runs.
    """
    with syntask_test_harness():
        yield


@pytest.fixture(scope="function")
def syntask_caplog(caplog):
    logger = logging.getLogger("syntask")

    # TODO: Determine a better pattern for this and expose for all tests
    logger.propagate = True

    try:
        yield caplog
    finally:
        logger.propagate = False


@pytest.fixture(scope="function")
def syntask_task_runs_caplog(syntask_caplog):
    logger = logging.getLogger("syntask.task_runs")

    # TODO: Determine a better pattern for this and expose for all tests
    logger.propagate = True

    try:
        yield syntask_caplog
    finally:
        logger.propagate = False
