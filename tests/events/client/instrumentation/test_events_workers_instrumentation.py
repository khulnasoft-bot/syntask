import pendulum
import pytest

from syntask import __version__
from syntask.client.orchestration import SyntaskClient
from syntask.events.clients import AssertingEventsClient
from syntask.events.worker import EventsWorker
from syntask.states import Cancelling, Scheduled
from syntask.testing.cli import invoke_and_assert
from syntask.testing.utilities import AsyncMock
from syntask.workers.base import BaseJobConfiguration, BaseWorker, BaseWorkerResult


class WorkerEventsTestImpl(BaseWorker):
    type = "events-test"
    job_configuration = BaseJobConfiguration

    async def run(self):
        pass

    async def kill_infrastructure(
        self,
        infrastructure_pid: str,
        configuration: BaseJobConfiguration,
        grace_seconds: int = 30,
    ):
        pass


async def test_worker_emits_submitted_event(
    asserting_events_worker: EventsWorker,
    reset_worker_events,
    syntask_client: SyntaskClient,
    worker_deployment_wq1,
    work_pool,
):
    flow_run = await syntask_client.create_flow_run_from_deployment(
        worker_deployment_wq1.id,
        state=Scheduled(scheduled_time=pendulum.now("utc")),
        tags=["flow-run-one"],
    )

    flow = await syntask_client.read_flow(flow_run.flow_id)

    async with WorkerEventsTestImpl(work_pool_name=work_pool.name) as worker:
        worker._work_pool = work_pool
        worker.run = AsyncMock()
        await worker.get_and_submit_flow_runs()

    await asserting_events_worker.drain()

    assert isinstance(asserting_events_worker._client, AssertingEventsClient)

    # When a worker submits a flow-run, it monitors that flow run until it's complete.
    # When it's complete, it fires a second 'monitored' event, which
    # is covered by the test_worker_emits_monitored_event below.
    assert len(asserting_events_worker._client.events) == 2

    submit_events = list(
        filter(
            lambda e: e.event == "syntask.worker.submitted-flow-run",
            asserting_events_worker._client.events,
        )
    )
    assert len(submit_events) == 1

    assert dict(submit_events[0].resource.items()) == {
        "syntask.resource.id": f"syntask.worker.events-test.{worker.get_name_slug()}",
        "syntask.resource.name": worker.name,
        "syntask.version": str(__version__),
        "syntask.worker-type": worker.type,
    }

    assert len(submit_events[0].related) == 6

    related = [dict(r.items()) for r in submit_events[0].related]

    assert related == [
        {
            "syntask.resource.id": f"syntask.deployment.{worker_deployment_wq1.id}",
            "syntask.resource.role": "deployment",
            "syntask.resource.name": worker_deployment_wq1.name,
        },
        {
            "syntask.resource.id": f"syntask.flow.{flow.id}",
            "syntask.resource.role": "flow",
            "syntask.resource.name": flow.name,
        },
        {
            "syntask.resource.id": f"syntask.flow-run.{flow_run.id}",
            "syntask.resource.role": "flow-run",
            "syntask.resource.name": flow_run.name,
        },
        {
            "syntask.resource.id": "syntask.tag.flow-run-one",
            "syntask.resource.role": "tag",
        },
        {
            "syntask.resource.id": "syntask.tag.test",
            "syntask.resource.role": "tag",
        },
        {
            "syntask.resource.id": f"syntask.work-pool.{work_pool.id}",
            "syntask.resource.role": "work-pool",
            "syntask.resource.name": work_pool.name,
        },
    ]


async def test_worker_emits_executed_event(
    asserting_events_worker: EventsWorker,
    reset_worker_events,
    syntask_client: SyntaskClient,
    worker_deployment_wq1,
    work_pool,
):
    flow_run = await syntask_client.create_flow_run_from_deployment(
        worker_deployment_wq1.id,
        state=Scheduled(scheduled_time=pendulum.now("utc")),
        tags=["flow-run-one"],
    )

    flow = await syntask_client.read_flow(flow_run.flow_id)

    worker_result = BaseWorkerResult(status_code=1, identifier="process123")
    run_flow_fn = AsyncMock(return_value=worker_result)

    async with WorkerEventsTestImpl(work_pool_name=work_pool.name) as worker:
        worker._work_pool = work_pool
        worker.run = run_flow_fn
        await worker.get_and_submit_flow_runs()

    await asserting_events_worker.drain()

    assert isinstance(asserting_events_worker._client, AssertingEventsClient)

    # When a worker submits a flow-run, it monitors that flow run until it's complete.
    # When it's complete, it fires a second 'submitted' event, which
    # is covered by the test_worker_emits_submitted_event below.
    assert len(asserting_events_worker._client.events) == 2

    submitted_events = list(
        filter(
            lambda e: e.event == "syntask.worker.submitted-flow-run",
            asserting_events_worker._client.events,
        )
    )
    assert len(submitted_events) == 1

    executed_events = list(
        filter(
            lambda e: e.event == "syntask.worker.executed-flow-run",
            asserting_events_worker._client.events,
        )
    )
    assert len(executed_events) == 1

    assert executed_events[0].event == "syntask.worker.executed-flow-run"

    assert dict(executed_events[0].resource.items()) == {
        "syntask.resource.id": f"syntask.worker.events-test.{worker.get_name_slug()}",
        "syntask.resource.name": worker.name,
        "syntask.version": str(__version__),
        "syntask.worker-type": worker.type,
    }

    assert len(executed_events[0].related) == 6

    related = [dict(r.items()) for r in executed_events[0].related]

    assert related == [
        {
            "syntask.resource.id": f"syntask.deployment.{worker_deployment_wq1.id}",
            "syntask.resource.role": "deployment",
            "syntask.resource.name": worker_deployment_wq1.name,
        },
        {
            "syntask.resource.id": f"syntask.flow.{flow.id}",
            "syntask.resource.role": "flow",
            "syntask.resource.name": flow.name,
        },
        {
            "syntask.resource.id": f"syntask.flow-run.{flow_run.id}",
            "syntask.resource.role": "flow-run",
            "syntask.resource.name": flow_run.name,
            "syntask.infrastructure.status-code": "1",
            "syntask.infrastructure.identifier": "process123",
        },
        {
            "syntask.resource.id": "syntask.tag.flow-run-one",
            "syntask.resource.role": "tag",
        },
        {
            "syntask.resource.id": "syntask.tag.test",
            "syntask.resource.role": "tag",
        },
        {
            "syntask.resource.id": f"syntask.work-pool.{work_pool.id}",
            "syntask.resource.role": "work-pool",
            "syntask.resource.name": work_pool.name,
        },
    ]

    assert executed_events[0].follows == submitted_events[0].id


@pytest.mark.usefixtures("use_hosted_api_server")
def test_lifecycle_events(
    asserting_events_worker: EventsWorker, reset_worker_events, work_pool
):
    invoke_and_assert(
        command=[
            "worker",
            "start",
            "--run-once",
            "-p",
            work_pool.name,
            "-n",
            "test-worker",
            "-t",
            "process",
        ],
        expected_code=0,
    )

    asserting_events_worker.drain()

    assert isinstance(asserting_events_worker._client, AssertingEventsClient)

    assert len(asserting_events_worker._client.events) == 2

    # first event will always be `syntask.worker.started`
    started_event = asserting_events_worker._client.events[0]
    assert started_event.event == "syntask.worker.started"

    assert dict(started_event.resource.items()) == {
        "syntask.resource.id": "syntask.worker.process.test-worker",
        "syntask.resource.name": "test-worker",
        "syntask.version": str(__version__),
        "syntask.worker-type": "process",
    }

    assert len(started_event.related) == 1

    related = [dict(r.items()) for r in started_event.related]

    assert related == [
        {
            "syntask.resource.id": f"syntask.work-pool.{work_pool.id}",
            "syntask.resource.role": "work-pool",
            "syntask.resource.name": work_pool.name,
        },
    ]

    # last event should be `syntask.worker.stopped`
    stopped_event = asserting_events_worker._client.events[
        len(asserting_events_worker._client.events) - 1
    ]
    assert stopped_event.event == "syntask.worker.stopped"

    assert dict(stopped_event.resource.items()) == {
        "syntask.resource.id": "syntask.worker.process.test-worker",
        "syntask.resource.name": "test-worker",
        "syntask.version": str(__version__),
        "syntask.worker-type": "process",
    }

    assert len(stopped_event.related) == 1

    related = [dict(r.items()) for r in stopped_event.related]

    assert related == [
        {
            "syntask.resource.id": f"syntask.work-pool.{work_pool.id}",
            "syntask.resource.role": "work-pool",
            "syntask.resource.name": work_pool.name,
        },
    ]


async def test_worker_emits_cancelled_event(
    asserting_events_worker: EventsWorker,
    reset_worker_events,
    syntask_client: SyntaskClient,
    worker_deployment_wq1,
    work_pool,
    disable_enhanced_cancellation,  # workers only cancel flow runs if enhanced cancellation is disabled
):
    flow_run = await syntask_client.create_flow_run_from_deployment(
        worker_deployment_wq1.id,
        state=Cancelling(),
        tags=["flow-run-one"],
    )
    await syntask_client.update_flow_run(flow_run.id, infrastructure_pid="process123")
    flow = await syntask_client.read_flow(flow_run.flow_id)

    async with WorkerEventsTestImpl(work_pool_name=work_pool.name) as worker:
        await worker.sync_with_backend()
        await worker.check_for_cancelled_flow_runs()

    await asserting_events_worker.drain()

    assert isinstance(asserting_events_worker._client, AssertingEventsClient)

    assert len(asserting_events_worker._client.events) == 1

    cancelled_events = list(
        filter(
            lambda e: e.event == "syntask.worker.cancelled-flow-run",
            asserting_events_worker._client.events,
        )
    )
    assert len(cancelled_events) == 1

    assert dict(cancelled_events[0].resource.items()) == {
        "syntask.resource.id": f"syntask.worker.events-test.{worker.get_name_slug()}",
        "syntask.resource.name": worker.name,
        "syntask.version": str(__version__),
        "syntask.worker-type": worker.type,
    }

    related = [dict(r.items()) for r in cancelled_events[0].related]

    assert related == [
        {
            "syntask.resource.id": f"syntask.deployment.{worker_deployment_wq1.id}",
            "syntask.resource.role": "deployment",
            "syntask.resource.name": worker_deployment_wq1.name,
        },
        {
            "syntask.resource.id": f"syntask.flow.{flow.id}",
            "syntask.resource.role": "flow",
            "syntask.resource.name": flow.name,
        },
        {
            "syntask.resource.id": f"syntask.flow-run.{flow_run.id}",
            "syntask.resource.role": "flow-run",
            "syntask.resource.name": flow_run.name,
            "syntask.infrastructure.identifier": "process123",
        },
        {
            "syntask.resource.id": "syntask.tag.flow-run-one",
            "syntask.resource.role": "tag",
        },
        {
            "syntask.resource.id": "syntask.tag.test",
            "syntask.resource.role": "tag",
        },
        {
            "syntask.resource.id": f"syntask.work-pool.{work_pool.id}",
            "syntask.resource.role": "work-pool",
            "syntask.resource.name": work_pool.name,
        },
    ]


def test_job_configuration_related_resources_no_objects():
    config = BaseJobConfiguration()
    config._related_objects = {
        "deployment": None,
        "flow": None,
        "flow-run": None,
    }
    assert config._related_resources() == []


async def test_worker_can_include_itself_as_related(work_pool):
    async with WorkerEventsTestImpl(work_pool_name=work_pool.name) as worker:
        await worker.sync_with_backend()

        related = [dict(r) for r in worker._event_related_resources(include_self=True)]

        assert related == [
            {
                "syntask.resource.id": f"syntask.work-pool.{work_pool.id}",
                "syntask.resource.role": "work-pool",
                "syntask.resource.name": work_pool.name,
            },
            {
                "syntask.resource.id": (
                    f"syntask.worker.events-test.{worker.get_name_slug()}"
                ),
                "syntask.resource.role": "worker",
                "syntask.resource.name": worker.name,
                "syntask.version": str(__version__),
                "syntask.worker-type": worker.type,
            },
        ]
