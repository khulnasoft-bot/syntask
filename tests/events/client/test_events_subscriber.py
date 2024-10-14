from typing import Optional, Type

import pytest
from websockets.exceptions import ConnectionClosedError

from syntask.events import Event, get_events_subscriber
from syntask.events.clients import (
    SyntaskCloudAccountEventSubscriber,
    SyntaskCloudEventSubscriber,
    SyntaskEventSubscriber,
)
from syntask.events.filters import EventFilter, EventNameFilter
from syntask.settings import (
    SYNTASK_API_KEY,
    SYNTASK_API_URL,
    SYNTASK_CLOUD_API_URL,
    SYNTASK_SERVER_ALLOW_EPHEMERAL_MODE,
    temporary_settings,
)
from syntask.testing.fixtures import Puppeteer, Recorder


@pytest.fixture
def ephemeral_settings():
    with temporary_settings(
        {
            SYNTASK_API_URL: None,
            SYNTASK_API_KEY: None,
            SYNTASK_CLOUD_API_URL: "https://cloudy/api",
            SYNTASK_SERVER_ALLOW_EPHEMERAL_MODE: True,
        }
    ):
        yield


@pytest.fixture
def server_settings():
    with temporary_settings(
        {
            SYNTASK_API_URL: "https://locally/api",
            SYNTASK_CLOUD_API_URL: "https://cloudy/api",
        }
    ):
        yield


async def test_constructs_server_client(server_settings):
    assert isinstance(get_events_subscriber(), SyntaskEventSubscriber)


async def test_constructs_client_when_ephemeral_enabled(ephemeral_settings):
    assert isinstance(get_events_subscriber(), SyntaskEventSubscriber)


def test_errors_when_missing_api_url_and_ephemeral_disabled():
    with temporary_settings(
        {
            SYNTASK_API_URL: None,
            SYNTASK_API_KEY: None,
            SYNTASK_CLOUD_API_URL: "https://cloudy/api",
            SYNTASK_SERVER_ALLOW_EPHEMERAL_MODE: False,
        }
    ):
        with pytest.raises(ValueError, match="SYNTASK_API_URL"):
            get_events_subscriber()


@pytest.fixture
def cloud_settings():
    with temporary_settings(
        {
            SYNTASK_API_URL: "https://cloudy/api/accounts/1/workspaces/2",
            SYNTASK_CLOUD_API_URL: "https://cloudy/api",
            SYNTASK_API_KEY: "howdy-doody",
        }
    ):
        yield


async def test_constructs_cloud_client(cloud_settings):
    assert isinstance(get_events_subscriber(), SyntaskCloudEventSubscriber)


def pytest_generate_tests(metafunc: pytest.Metafunc):
    fixtures = set(metafunc.fixturenames)

    cloud_subscribers = [
        (
            SyntaskCloudEventSubscriber,
            "/accounts/A/workspaces/W/events/out",
            "my-token",
        ),
        (SyntaskCloudAccountEventSubscriber, "/accounts/A/events/out", "my-token"),
    ]
    subscribers = [
        # The base subscriber for OSS will just use the API URL, which is set to a
        # Cloud URL here, but it would usually be just /events/out
        (SyntaskEventSubscriber, "/accounts/A/workspaces/W/events/out", None),
    ] + cloud_subscribers

    if "Subscriber" in fixtures:
        metafunc.parametrize("Subscriber,socket_path,token", subscribers)
    elif "CloudSubscriber" in fixtures:
        metafunc.parametrize("CloudSubscriber,socket_path,token", cloud_subscribers)


@pytest.fixture(autouse=True)
def api_setup(events_cloud_api_url: str):
    with temporary_settings(
        updates={
            SYNTASK_API_URL: events_cloud_api_url,
            SYNTASK_API_KEY: "my-token",
        }
    ):
        yield


async def test_subscriber_can_connect_with_defaults(
    Subscriber: Type[SyntaskEventSubscriber],
    socket_path: str,
    token: Optional[str],
    example_event_1: Event,
    example_event_2: Event,
    recorder: Recorder,
    puppeteer: Puppeteer,
):
    puppeteer.token = token
    puppeteer.outgoing_events = [example_event_1, example_event_2]

    async with Subscriber() as subscriber:
        async for event in subscriber:
            recorder.events.append(event)

    assert recorder.connections == 1
    assert recorder.path == socket_path
    assert recorder.events == [example_event_1, example_event_2]
    assert recorder.token == puppeteer.token
    assert subscriber._filter
    assert recorder.filter == subscriber._filter


async def test_cloud_subscriber_complains_without_api_url_and_key(
    CloudSubscriber: Type[SyntaskCloudEventSubscriber],
    socket_path: str,
    token: Optional[str],
    example_event_1: Event,
    example_event_2: Event,
    recorder: Recorder,
    puppeteer: Puppeteer,
):
    with temporary_settings(updates={SYNTASK_API_KEY: "", SYNTASK_API_URL: ""}):
        with pytest.raises(ValueError, match="must be provided or set"):
            CloudSubscriber()


async def test_subscriber_can_connect_and_receive_one_event(
    Subscriber: Type[SyntaskEventSubscriber],
    socket_path: str,
    token: Optional[str],
    example_event_1: Event,
    example_event_2: Event,
    recorder: Recorder,
    puppeteer: Puppeteer,
):
    puppeteer.token = token
    puppeteer.outgoing_events = [example_event_1, example_event_2]

    filter = EventFilter(event=EventNameFilter(name=["example.event"]))

    async with Subscriber(
        filter=filter,
        reconnection_attempts=0,
    ) as subscriber:
        async for event in subscriber:
            recorder.events.append(event)

    assert recorder.connections == 1
    assert recorder.path == socket_path
    assert recorder.events == [example_event_1, example_event_2]
    assert recorder.token == puppeteer.token
    assert recorder.filter == filter


async def test_subscriber_specifying_negative_reconnects_gets_error(
    Subscriber: Type[SyntaskEventSubscriber],
    socket_path: str,
    token: Optional[str],
    example_event_1: Event,
    example_event_2: Event,
    recorder: Recorder,
    puppeteer: Puppeteer,
):
    puppeteer.token = token
    puppeteer.outgoing_events = [example_event_1, example_event_2]

    filter = EventFilter(event=EventNameFilter(name=["example.event"]))

    with pytest.raises(ValueError, match="non-negative"):
        Subscriber(
            filter=filter,
            reconnection_attempts=-1,
        )

    assert recorder.connections == 0


async def test_subscriber_raises_on_invalid_auth_with_soft_denial(
    CloudSubscriber: Type[SyntaskCloudEventSubscriber],
    socket_path: str,
    token: Optional[str],
    events_cloud_api_url: str,
    example_event_1: Event,
    example_event_2: Event,
    recorder: Recorder,
    puppeteer: Puppeteer,
):
    puppeteer.token = "my-token"
    puppeteer.outgoing_events = [example_event_1, example_event_2]

    filter = EventFilter(event=EventNameFilter(name=["example.event"]))

    with pytest.raises(Exception, match="Unable to authenticate"):
        subscriber = CloudSubscriber(
            events_cloud_api_url,
            "bogus",
            filter=filter,
            reconnection_attempts=0,
        )
        await subscriber.__aenter__()

    assert recorder.connections == 1
    assert recorder.path == socket_path
    assert recorder.token == "bogus"
    assert recorder.events == []


async def test_cloud_subscriber_raises_on_invalid_auth_with_hard_denial(
    CloudSubscriber: Type[SyntaskCloudEventSubscriber],
    socket_path: str,
    token: Optional[str],
    events_cloud_api_url: str,
    example_event_1: Event,
    example_event_2: Event,
    recorder: Recorder,
    puppeteer: Puppeteer,
):
    puppeteer.hard_auth_failure = True
    puppeteer.token = "my-token"
    puppeteer.outgoing_events = [example_event_1, example_event_2]

    filter = EventFilter(event=EventNameFilter(name=["example.event"]))

    with pytest.raises(Exception, match="Unable to authenticate"):
        subscriber = CloudSubscriber(
            events_cloud_api_url,
            "bogus",
            filter=filter,
            reconnection_attempts=0,
        )
        await subscriber.__aenter__()

    assert recorder.connections == 1
    assert recorder.path == socket_path
    assert recorder.token == "bogus"
    assert recorder.events == []


async def test_subscriber_reconnects_on_hard_disconnects(
    Subscriber: Type[SyntaskEventSubscriber],
    socket_path: str,
    token: Optional[str],
    example_event_1: Event,
    example_event_2: Event,
    recorder: Recorder,
    puppeteer: Puppeteer,
):
    puppeteer.token = token
    puppeteer.outgoing_events = [example_event_1, example_event_2]
    puppeteer.hard_disconnect_after = example_event_1.id

    filter = EventFilter(event=EventNameFilter(name=["example.event"]))

    async with Subscriber(
        filter=filter,
        reconnection_attempts=2,
    ) as subscriber:
        async for event in subscriber:
            recorder.events.append(event)

    assert recorder.connections == 2
    assert recorder.events == [example_event_1, example_event_2]


async def test_subscriber_gives_up_after_so_many_attempts(
    Subscriber: Type[SyntaskEventSubscriber],
    socket_path: str,
    token: Optional[str],
    example_event_1: Event,
    example_event_2: Event,
    recorder: Recorder,
    puppeteer: Puppeteer,
):
    puppeteer.token = token
    puppeteer.outgoing_events = [example_event_1, example_event_2]
    puppeteer.hard_disconnect_after = example_event_1.id

    filter = EventFilter(event=EventNameFilter(name=["example.event"]))

    with pytest.raises(ConnectionClosedError):
        async with Subscriber(
            filter=filter,
            reconnection_attempts=4,
        ) as subscriber:
            async for event in subscriber:
                puppeteer.refuse_any_further_connections = True
                recorder.events.append(event)

    assert recorder.connections == 1 + 4


async def test_subscriber_skips_duplicate_events(
    Subscriber: Type[SyntaskEventSubscriber],
    socket_path: str,
    token: Optional[str],
    example_event_1: Event,
    example_event_2: Event,
    recorder: Recorder,
    puppeteer: Puppeteer,
):
    puppeteer.token = token
    puppeteer.outgoing_events = [example_event_1, example_event_1, example_event_2]

    filter = EventFilter(event=EventNameFilter(name=["example.event"]))

    async with Subscriber(filter=filter) as subscriber:
        async for event in subscriber:
            recorder.events.append(event)

    assert recorder.events == [example_event_1, example_event_2]
