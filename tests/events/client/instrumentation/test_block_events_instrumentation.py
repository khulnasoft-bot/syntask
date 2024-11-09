from unittest import mock

from syntask._internal.pydantic import HAS_PYDANTIC_V2

if HAS_PYDANTIC_V2:
    from pydantic.v1 import SecretStr
else:
    from pydantic import SecretStr

from syntask.blocks.notifications import PagerDutyWebHook
from syntask.blocks.system import Secret
from syntask.events.clients import AssertingEventsClient
from syntask.events.worker import EventsWorker
from syntask.testing.utilities import AsyncMock


async def test_async_blocks_instrumented(
    asserting_events_worker: EventsWorker, reset_worker_events
):
    secret = Secret(value=SecretStr("I'm hidden!"))
    document_id = await secret.save("top-secret", overwrite=True)
    secret = await Secret.load("top-secret")
    secret.get()

    await asserting_events_worker.drain()

    assert isinstance(asserting_events_worker._client, AssertingEventsClient)
    assert len(asserting_events_worker._client.events) == 3

    save_event = asserting_events_worker._client.events[0]
    assert save_event.event == "syntask.block.secret.save.called"
    assert save_event.resource.id == f"syntask.block-document.{document_id}"
    assert save_event.resource["syntask.resource.name"] == "top-secret"
    assert save_event.related[0].id == "syntask.block-type.secret"
    assert save_event.related[0].role == "block-type"

    load_event = asserting_events_worker._client.events[1]
    assert load_event.event == "syntask.block.secret.load.called"
    assert load_event.resource.id == f"syntask.block-document.{document_id}"
    assert load_event.resource["syntask.resource.name"] == "top-secret"
    assert load_event.related[0].id == "syntask.block-type.secret"
    assert load_event.related[0].role == "block-type"

    get_event = asserting_events_worker._client.events[2]
    assert get_event.event == "syntask.block.secret.get.called"
    assert get_event.resource.id == f"syntask.block-document.{document_id}"
    assert get_event.resource["syntask.resource.name"] == "top-secret"
    assert get_event.related[0].id == "syntask.block-type.secret"
    assert get_event.related[0].role == "block-type"


def test_sync_blocks_instrumented(
    asserting_events_worker: EventsWorker, reset_worker_events
):
    secret = Secret(value=SecretStr("I'm hidden!"))
    document_id = secret.save("top-secret", overwrite=True)
    secret = Secret.load("top-secret")
    secret.get()

    asserting_events_worker.drain()

    assert isinstance(asserting_events_worker._client, AssertingEventsClient)
    assert len(asserting_events_worker._client.events) == 3

    save_event = asserting_events_worker._client.events[0]
    assert save_event.event == "syntask.block.secret.save.called"
    assert save_event.resource.id == f"syntask.block-document.{document_id}"
    assert save_event.resource["syntask.resource.name"] == "top-secret"
    assert save_event.related[0].id == "syntask.block-type.secret"
    assert save_event.related[0].role == "block-type"

    load_event = asserting_events_worker._client.events[1]
    assert load_event.event == "syntask.block.secret.load.called"
    assert load_event.resource.id == f"syntask.block-document.{document_id}"
    assert load_event.resource["syntask.resource.name"] == "top-secret"
    assert load_event.related[0].id == "syntask.block-type.secret"
    assert load_event.related[0].role == "block-type"

    get_event = asserting_events_worker._client.events[2]
    assert get_event.event == "syntask.block.secret.get.called"
    assert get_event.resource.id == f"syntask.block-document.{document_id}"
    assert get_event.resource["syntask.resource.name"] == "top-secret"
    assert get_event.related[0].id == "syntask.block-type.secret"
    assert get_event.related[0].role == "block-type"


def test_notifications_notify_instrumented_sync(
    asserting_events_worker: EventsWorker, reset_worker_events
):
    with mock.patch("apprise.Apprise", autospec=True) as AppriseMock:
        apprise_instance_mock = AppriseMock.return_value
        apprise_instance_mock.async_notify = AsyncMock()

        block = PagerDutyWebHook(
            integration_key=SecretStr("integration_key"), api_key=SecretStr("api_key")
        )
        document_id = block.save("pager-duty-events", overwrite=True)

        pgduty = PagerDutyWebHook.load("pager-duty-events")
        pgduty.notify("Oh, we're you sleeping?")

        asserting_events_worker.drain()

        assert isinstance(asserting_events_worker._client, AssertingEventsClient)
        assert len(asserting_events_worker._client.events) == 3

        save_event = asserting_events_worker._client.events[0]
        assert save_event.event == "syntask.block.pager-duty-webhook.save.called"
        assert save_event.resource.id == f"syntask.block-document.{document_id}"
        assert save_event.resource["syntask.resource.name"] == "pager-duty-events"
        assert save_event.related[0].id == "syntask.block-type.pager-duty-webhook"
        assert save_event.related[0].role == "block-type"

        load_event = asserting_events_worker._client.events[1]
        assert load_event.event == "syntask.block.pager-duty-webhook.load.called"
        assert load_event.resource.id == f"syntask.block-document.{document_id}"
        assert load_event.resource["syntask.resource.name"] == "pager-duty-events"
        assert load_event.related[0].id == "syntask.block-type.pager-duty-webhook"
        assert load_event.related[0].role == "block-type"

        notify_event = asserting_events_worker._client.events[2]
        assert notify_event.event == "syntask.block.pager-duty-webhook.notify.called"
        assert notify_event.resource.id == f"syntask.block-document.{document_id}"
        assert notify_event.resource["syntask.resource.name"] == "pager-duty-events"
        assert notify_event.related[0].id == "syntask.block-type.pager-duty-webhook"
        assert notify_event.related[0].role == "block-type"


async def test_notifications_notify_instrumented_async(
    asserting_events_worker: EventsWorker, reset_worker_events
):
    with mock.patch("apprise.Apprise", autospec=True) as AppriseMock:
        apprise_instance_mock = AppriseMock.return_value
        apprise_instance_mock.async_notify = AsyncMock()

        block = PagerDutyWebHook(
            integration_key=SecretStr("integration_key"), api_key=SecretStr("api_key")
        )
        document_id = await block.save("pager-duty-events", overwrite=True)

        pgduty = await PagerDutyWebHook.load("pager-duty-events")
        await pgduty.notify("Oh, we're you sleeping?")

        await asserting_events_worker.drain()

        assert isinstance(asserting_events_worker._client, AssertingEventsClient)
        assert len(asserting_events_worker._client.events) == 3

        save_event = asserting_events_worker._client.events[0]
        assert save_event.event == "syntask.block.pager-duty-webhook.save.called"
        assert save_event.resource.id == f"syntask.block-document.{document_id}"
        assert save_event.resource["syntask.resource.name"] == "pager-duty-events"
        assert save_event.related[0].id == "syntask.block-type.pager-duty-webhook"
        assert save_event.related[0].role == "block-type"

        load_event = asserting_events_worker._client.events[1]
        assert load_event.event == "syntask.block.pager-duty-webhook.load.called"
        assert load_event.resource.id == f"syntask.block-document.{document_id}"
        assert load_event.resource["syntask.resource.name"] == "pager-duty-events"
        assert load_event.related[0].id == "syntask.block-type.pager-duty-webhook"
        assert load_event.related[0].role == "block-type"

        notify_event = asserting_events_worker._client.events[2]
        assert notify_event.event == "syntask.block.pager-duty-webhook.notify.called"
        assert notify_event.resource.id == f"syntask.block-document.{document_id}"
        assert notify_event.resource["syntask.resource.name"] == "pager-duty-events"
        assert notify_event.related[0].id == "syntask.block-type.pager-duty-webhook"
        assert notify_event.related[0].role == "block-type"
