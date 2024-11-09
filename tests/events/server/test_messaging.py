from typing import Generator, Type
from unittest import mock
from uuid import uuid4

import pendulum
import pytest

from syntask.server.events import messaging
from syntask.server.events.messaging import create_event_publisher
from syntask.server.events.schemas.events import ReceivedEvent, Resource
from syntask.server.utilities.messaging import CapturingPublisher
from syntask.settings import SYNTASK_EVENTS_MAXIMUM_SIZE_BYTES, temporary_settings

from .conftest import assert_message_represents_event


@pytest.fixture
def event1() -> ReceivedEvent:
    return ReceivedEvent(
        occurred=pendulum.now("UTC"),
        event="was.tubular",
        resource=Resource.parse_obj({"syntask.resource.id": "my.kickflip"}),
        payload={"goodbye": "yellow brick road"},
        id=uuid4(),
    )


@pytest.fixture
def event2() -> ReceivedEvent:
    return ReceivedEvent(
        occurred=pendulum.now("UTC"),
        event="was.super.gnarly",
        resource=Resource.parse_obj({"syntask.resource.id": "my.ollie"}),
        payload={"where": "the dogs of society howl"},
        id=uuid4(),
    )


@pytest.fixture
def event3() -> ReceivedEvent:
    return ReceivedEvent(
        occurred=pendulum.now("UTC"),
        event="was.extra.spicy",
        resource=Resource.parse_obj({"syntask.resource.id": "my.heelflip"}),
        payload={"you": "can't plant me in your penthouse"},
        id=uuid4(),
    )


@pytest.fixture
def capturing_publisher() -> Generator[Type[CapturingPublisher], None, None]:
    with mock.patch(
        "syntask.server.events.messaging.create_publisher",
        CapturingPublisher,
    ):
        CapturingPublisher.messages = []
        yield CapturingPublisher
        CapturingPublisher.messages = []


async def test_publishing_events(
    capturing_publisher: Type[CapturingPublisher],
    event1: ReceivedEvent,
    event2: ReceivedEvent,
):
    async with create_event_publisher() as publisher:
        await publisher.publish_event(event1)
        await publisher.publish_event(event2)

    (one, two) = capturing_publisher.messages

    assert_message_represents_event(one, event1)
    assert_message_represents_event(two, event2)


@pytest.fixture
def tiny_event_size() -> Generator[int, None, None]:
    with temporary_settings(updates={SYNTASK_EVENTS_MAXIMUM_SIZE_BYTES: 10000}):
        yield 10_000


async def test_maximum_event_message_size(
    capturing_publisher: Type[CapturingPublisher],
    event1: ReceivedEvent,
    event2: ReceivedEvent,
    event3: ReceivedEvent,
    caplog: pytest.LogCaptureFixture,
    tiny_event_size: int,
):
    with caplog.at_level("WARN"):
        async with create_event_publisher() as publisher:
            await publisher.publish_event(event1)

            # publish a bad one in the middle that will be quietly dropped
            event2.payload = {"message": "foo" * tiny_event_size}
            await publisher.publish_event(event2)

            await publisher.publish_event(event3)

    assert "Refusing to publish event" in caplog.text

    (one, two) = capturing_publisher.messages

    assert_message_represents_event(one, event1)
    assert_message_represents_event(two, event3)


async def test_will_not_publish_duplicate_messages(
    capturing_publisher: Type[CapturingPublisher],
    event1: ReceivedEvent,
    event2: ReceivedEvent,
    event3: ReceivedEvent,
):
    await messaging.publish([event1, event2])
    # send event2 a few more times, in different batches to confirm that we aren't
    # just deduping locally to each batch
    await messaging.publish([event2])
    await messaging.publish([event2])
    await messaging.publish([event2])
    # bookend it with event3 to make sure all the events come through
    await messaging.publish([event1, event2, event3])

    (one, two, three) = capturing_publisher.messages

    assert_message_represents_event(one, event1)
    assert_message_represents_event(two, event2)
    assert_message_represents_event(three, event3)
