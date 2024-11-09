import uuid
from typing import Dict, List, Union
from unittest import mock

import httpx
import pytest

from syntask import flow
from syntask.client.schemas.objects import FlowRun
from syntask.runner import submit_to_runner
from syntask.settings import (
    SYNTASK_EXPERIMENTAL_ENABLE_EXTRA_RUNNER_ENDPOINTS,
    SYNTASK_RUNNER_SERVER_ENABLE,
    temporary_settings,
)
from syntask.states import Running


@flow
def identity(whatever):
    return whatever


@flow
async def async_identity(whatever):
    return whatever


@flow
def super_identity(*args, **kwargs):
    return args, kwargs


@flow(log_prints=True)
def independent():
    print("i don't need no stinkin' parameters")


@pytest.fixture
def mock_webserver(monkeypatch):
    async def mock_submit_flow_to_runner(_, parameters, *__):
        return FlowRun(flow_id=uuid.uuid4(), state=Running(), parameters=parameters)

    monkeypatch.setattr(
        "syntask.runner.submit._submit_flow_to_runner", mock_submit_flow_to_runner
    )


@pytest.fixture
def mock_webserver_not_running(monkeypatch):
    async def mock_submit_flow_to_runner(*_, **__):
        raise httpx.ConnectError("Mocked connection error")

    monkeypatch.setattr(
        "syntask.runner.submit._submit_flow_to_runner", mock_submit_flow_to_runner
    )


@pytest.fixture(autouse=True)
def runner_settings():
    with temporary_settings(
        {
            SYNTASK_RUNNER_SERVER_ENABLE: True,
            SYNTASK_EXPERIMENTAL_ENABLE_EXTRA_RUNNER_ENDPOINTS: True,
        }
    ):
        yield


def test_submission_raises_if_extra_endpoints_not_enabled(mock_webserver):
    with temporary_settings(
        {SYNTASK_EXPERIMENTAL_ENABLE_EXTRA_RUNNER_ENDPOINTS: False}
    ):
        with pytest.raises(
            ValueError,
            match=(
                "The `submit_to_runner` utility requires the `Runner` webserver to be"
                " running and built with extra endpoints enabled."
            ),
        ):
            submit_to_runner(identity, {"whatever": 42})


@pytest.mark.parametrize("syntask_callable", [identity, async_identity])
def test_submit_to_runner_happy_path_sync_context(mock_webserver, syntask_callable):
    flow_run = submit_to_runner(syntask_callable, {"whatever": 42})

    assert flow_run.state.is_running()
    assert flow_run.parameters == {"whatever": 42}


@pytest.mark.parametrize("syntask_callable", [identity, async_identity])
async def test_submit_to_runner_happy_path_async_context(
    mock_webserver, syntask_callable
):
    flow_run = await submit_to_runner(syntask_callable, {"whatever": 42})

    assert flow_run.state.is_running()
    assert flow_run.parameters == {"whatever": 42}


async def test_submit_to_runner_raises_if_not_syntask_callable():
    with pytest.raises(
        TypeError,
        match=(
            "The `submit_to_runner` utility only supports submitting flows and tasks."
        ),
    ):
        await submit_to_runner(lambda: None)


async def test_submission_with_optional_parameters(mock_webserver):
    flow_run = await submit_to_runner(independent)

    assert flow_run.state.is_running()
    assert flow_run.parameters == {}


def test_submission_raises_if_webserver_not_running(mock_webserver_not_running):
    with temporary_settings({SYNTASK_RUNNER_SERVER_ENABLE: False}):
        with pytest.raises(
            (httpx.ConnectTimeout, RuntimeError),
            match="Ensure that the server is running",
        ):
            submit_to_runner(identity, {"d": {"input": 9001}})


@pytest.mark.parametrize("input_", [[{"input": 1}, {"input": 2}], {"input": 3}])
def test_return_for_submissions_matches_input(
    mock_webserver, input_: Union[List[Dict], Dict]
):
    def _flow_run_generator(*_, **__):
        return FlowRun(flow_id=uuid.uuid4())

    with mock.patch(
        "syntask.runner.submit._submit_flow_to_runner",
        side_effect=_flow_run_generator,
    ):
        results = submit_to_runner(identity, input_)

        if isinstance(input_, dict):
            assert isinstance(results, FlowRun)
        else:
            assert len(results) == len(input_)
            assert all(isinstance(r, FlowRun) for r in results)


@pytest.mark.parametrize(
    "input_",
    [
        {
            "name": "Schleeb",
            "age": 99,
            "young": True,
            "metadata": [{"nested": "info"}],
            "data": [True, False, True],
            "info": {"nested": "info"},
        },
        [
            {
                "name": "Schleeb",
                "age": 99,
                "young": True,
                "metadata": [{"nested": "info"}],
                "data": [True, False, True],
                "info": {"nested": "info"},
            }
        ],
        [
            {
                "name": "Schleeb",
                "age": 99,
                "young": True,
                "metadata": [{"nested": "info"}],
                "data": [True, False, True],
                "info": {"nested": "info"},
            }
        ],
        [{"1": {2: {3: {4: None}}}}],
    ],
)
def test_types_in_submission(mock_webserver, input_: Union[List[Dict], Dict]):
    results = submit_to_runner(super_identity, input_)

    if isinstance(input_, List):
        assert len(results) == len(input_)
        for r in results:
            assert isinstance(r, FlowRun)
    else:
        assert isinstance(results, FlowRun)
