import pytest
from websockets.exceptions import ConnectionClosedError

from syntask.events import Event
from syntask.events.clients import SyntaskCloudEventSubscriber
from syntask.events.filters import EventFilter, EventNameFilter
from syntask.settings import SYNTASK_API_KEY, SYNTASK_API_URL, temporary_settings
from syntask.testing.fixtures import Puppeteer, Recorder


async def test_subscriber_can_connect_with_defaults(
    events_cloud_api_url: str,
    example_event_1: Event,
    example_event_2: Event,
    recorder: Recorder,
    puppeteer: Puppeteer,
):
    with temporary_settings(
        updates={SYNTASK_API_KEY: "my-token", SYNTASK_API_URL: events_cloud_api_url}
    ):
        puppeteer.token = "my-token"
        puppeteer.outgoing_events = [example_event_1, example_event_2]

        async with SyntaskCloudEventSubscriber() as subscriber:
            async for event in subscriber:
                recorder.events.append(event)

        assert recorder.connections == 1
        assert recorder.path == "/accounts/A/workspaces/W/events/out"
        assert recorder.events == [example_event_1, example_event_2]
        assert recorder.token == "my-token"
        assert subscriber._filter
        assert recorder.filter == subscriber._filter


async def test_subscriber_complains_without_api_url_and_key(
    events_cloud_api_url: str,
    example_event_1: Event,
    example_event_2: Event,
    recorder: Recorder,
    puppeteer: Puppeteer,
):
    with temporary_settings(updates={SYNTASK_API_KEY: "", SYNTASK_API_URL: ""}):
        with pytest.raises(ValueError, match="must be provided or set"):
            SyntaskCloudEventSubscriber()


async def test_subscriber_can_connect_and_receive_one_event(
    events_cloud_api_url: str,
    example_event_1: Event,
    example_event_2: Event,
    recorder: Recorder,
    puppeteer: Puppeteer,
):
    puppeteer.token = "my-token"
    puppeteer.outgoing_events = [example_event_1, example_event_2]

    filter = EventFilter(event=EventNameFilter(name=["example.event"]))

    async with SyntaskCloudEventSubscriber(
        events_cloud_api_url,
        "my-token",
        filter,
        reconnection_attempts=0,
    ) as subscriber:
        async for event in subscriber:
            recorder.events.append(event)

    assert recorder.connections == 1
    assert recorder.path == "/accounts/A/workspaces/W/events/out"
    assert recorder.events == [example_event_1, example_event_2]
    assert recorder.token == "my-token"
    assert recorder.filter == filter


async def test_subscriber_specifying_negative_reconnects_gets_error(
    events_cloud_api_url: str,
    example_event_1: Event,
    example_event_2: Event,
    recorder: Recorder,
    puppeteer: Puppeteer,
):
    puppeteer.token = "my-token"
    puppeteer.outgoing_events = [example_event_1, example_event_2]

    filter = EventFilter(event=EventNameFilter(name=["example.event"]))

    with pytest.raises(ValueError, match="non-negative"):
        SyntaskCloudEventSubscriber(
            events_cloud_api_url,
            "my-token",
            filter,
            reconnection_attempts=-1,
        )

    assert recorder.connections == 0


async def test_subscriber_raises_on_invalid_auth_with_soft_denial(
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
        subscriber = SyntaskCloudEventSubscriber(
            events_cloud_api_url,
            "bogus",
            filter,
            reconnection_attempts=0,
        )
        await subscriber.__aenter__()

    assert recorder.connections == 1
    assert recorder.path == "/accounts/A/workspaces/W/events/out"
    assert recorder.token == "bogus"
    assert recorder.events == []


async def test_subscriber_raises_on_invalid_auth_with_hard_denial(
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
        subscriber = SyntaskCloudEventSubscriber(
            events_cloud_api_url,
            "bogus",
            filter,
            reconnection_attempts=0,
        )
        await subscriber.__aenter__()

    assert recorder.connections == 1
    assert recorder.path == "/accounts/A/workspaces/W/events/out"
    assert recorder.token == "bogus"
    assert recorder.events == []


async def test_subscriber_reconnects_on_hard_disconnects(
    events_cloud_api_url: str,
    example_event_1: Event,
    example_event_2: Event,
    recorder: Recorder,
    puppeteer: Puppeteer,
):
    puppeteer.token = "my-token"
    puppeteer.outgoing_events = [example_event_1, example_event_2]
    puppeteer.hard_disconnect_after = example_event_1.id

    filter = EventFilter(event=EventNameFilter(name=["example.event"]))

    async with SyntaskCloudEventSubscriber(
        events_cloud_api_url,
        "my-token",
        filter,
        reconnection_attempts=2,
    ) as subscriber:
        async for event in subscriber:
            recorder.events.append(event)

    assert recorder.connections == 2
    assert recorder.events == [example_event_1, example_event_2]


async def test_subscriber_gives_up_after_so_many_attempts(
    events_cloud_api_url: str,
    example_event_1: Event,
    example_event_2: Event,
    recorder: Recorder,
    puppeteer: Puppeteer,
):
    puppeteer.token = "my-token"
    puppeteer.outgoing_events = [example_event_1, example_event_2]
    puppeteer.hard_disconnect_after = example_event_1.id

    filter = EventFilter(event=EventNameFilter(name=["example.event"]))

    with pytest.raises(ConnectionClosedError):
        async with SyntaskCloudEventSubscriber(
            events_cloud_api_url,
            "my-token",
            filter,
            reconnection_attempts=4,
        ) as subscriber:
            async for event in subscriber:
                puppeteer.refuse_any_further_connections = True
                recorder.events.append(event)

    assert recorder.connections == 1 + 4


async def test_subscriber_skips_duplicate_events(
    events_cloud_api_url: str,
    example_event_1: Event,
    example_event_2: Event,
    recorder: Recorder,
    puppeteer: Puppeteer,
):
    puppeteer.token = "my-token"
    puppeteer.outgoing_events = [example_event_1, example_event_1, example_event_2]

    filter = EventFilter(event=EventNameFilter(name=["example.event"]))

    async with SyntaskCloudEventSubscriber(
        events_cloud_api_url,
        "my-token",
        filter,
    ) as subscriber:
        async for event in subscriber:
            recorder.events.append(event)

    assert recorder.events == [example_event_1, example_event_2]
