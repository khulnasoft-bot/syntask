import pytest

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
