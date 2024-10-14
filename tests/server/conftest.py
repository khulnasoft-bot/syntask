import pytest

from syntask.server.utilities.messaging import create_cache
from syntask.server.utilities.messaging.memory import Topic
from syntask.settings import (
    SYNTASK_MESSAGING_BROKER,
    SYNTASK_MESSAGING_CACHE,
    temporary_settings,
)

# Use the in-memory implementation of the cache and message broker for server testing


@pytest.fixture(autouse=True)
def events_configuration():
    with temporary_settings(
        {
            SYNTASK_MESSAGING_CACHE: "syntask.server.utilities.messaging.memory",
            SYNTASK_MESSAGING_BROKER: "syntask.server.utilities.messaging.memory",
        }
    ):
        yield


@pytest.fixture(autouse=True)
def clear_topics(events_configuration: None):
    Topic.clear_all()
    yield
    Topic.clear_all()


@pytest.fixture(autouse=True)
async def reset_recently_seen_messages(events_configuration: None):
    cache = create_cache()
    await cache.clear_recently_seen_messages()
    yield
    await cache.clear_recently_seen_messages()
