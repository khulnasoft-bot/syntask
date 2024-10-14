import pytest

from syntask.events.worker import EventsWorker
from syntask.server.events.clients import AssertingEventsClient


@pytest.fixture
def clean_asserting_events_client():
    AssertingEventsClient.last = None
    AssertingEventsClient.all.clear()


@pytest.fixture(autouse=True)
def workspace_events_client(
    clean_asserting_events_client: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "syntask.server.events.clients.SyntaskServerEventsClient",
        AssertingEventsClient,
    )
    monkeypatch.setattr(
        "syntask.server.events.actions.SyntaskServerEventsClient",
        AssertingEventsClient,
    )
    monkeypatch.setattr(
        "syntask.server.orchestration.instrumentation_policies.SyntaskServerEventsClient",
        AssertingEventsClient,
    )
    monkeypatch.setattr(
        "syntask.server.models.deployments.SyntaskServerEventsClient",
        AssertingEventsClient,
    )


@pytest.fixture(scope="session", autouse=True)
async def drain_events_workers():
    """
    Ensure that all workers have finished before the test session ends.
    """
    yield
    await EventsWorker.drain_all()
