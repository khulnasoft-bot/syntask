import pendulum

from syntask import flow, task
from syntask.client.orchestration import SyntaskClient
from syntask.client.schemas.objects import State
from syntask.events.clients import AssertingEventsClient
from syntask.events.schemas.events import Resource
from syntask.events.worker import EventsWorker
from syntask.filesystems import LocalFileSystem
from syntask.task_worker import TaskWorker


async def test_task_state_change_happy_path(
    asserting_events_worker: EventsWorker,
    reset_worker_events: None,
    syntask_client: SyntaskClient,
    events_pipeline,
):
    @task
    def happy_little_tree():
        return "🌳"

    @flow
    def happy_path():
        return happy_little_tree(return_state=True)

    flow_state: State[State[str]] = happy_path(return_state=True)

    await events_pipeline.process_events(dequeue_events=False)

    task_state: State[str] = await flow_state.result()
    task_run_id = task_state.state_details.task_run_id

    task_run = await syntask_client.read_task_run(task_run_id)
    task_run_states = await syntask_client.read_task_run_states(task_run_id)

    await asserting_events_worker.drain()
    assert isinstance(asserting_events_worker._client, AssertingEventsClient)
    events = [
        event
        for event in asserting_events_worker._client.events
        if event.event.startswith("syntask.task-run.")
    ]
    assert len(task_run_states) == len(events) == 3

    pending, running, completed = events

    assert pending.event == "syntask.task-run.Pending"
    assert pending.id == task_run_states[0].id
    assert pending.occurred == task_run_states[0].timestamp
    assert pending.resource == Resource(
        {
            "syntask.resource.id": f"syntask.task-run.{task_run.id}",
            "syntask.resource.name": task_run.name,
            "syntask.state-message": "",
            "syntask.state-type": "PENDING",
            "syntask.state-name": "Pending",
            "syntask.state-timestamp": task_run_states[0].timestamp.isoformat(),
            "syntask.orchestration": "client",
        }
    )
    assert (
        pendulum.parse(pending.payload["task_run"].pop("expected_start_time"))
        == task_run.expected_start_time
    )
    assert pending.payload["task_run"].pop("task_key").startswith("happy_little_tree")
    assert pending.payload == {
        "initial_state": None,
        "intended": {"from": None, "to": "PENDING"},
        "validated_state": {
            "type": "PENDING",
            "name": "Pending",
            "message": "",
            "state_details": {},
            "data": None,
        },
        "task_run": {
            "dynamic_key": task_run.dynamic_key,
            "empirical_policy": {
                "max_retries": 0,
                "retries": 0,
                "retry_delay": 0,
                "retry_delay_seconds": 0.0,
            },
            "flow_run_run_count": 0,
            "name": task_run.name,
            "run_count": 0,
            "tags": [],
            "task_inputs": {},
            "total_run_time": 0.0,
        },
    }

    assert running.event == "syntask.task-run.Running"
    assert running.id == task_run_states[1].id
    assert running.occurred == task_run_states[1].timestamp
    assert running.resource == Resource(
        {
            "syntask.resource.id": f"syntask.task-run.{task_run.id}",
            "syntask.resource.name": task_run.name,
            "syntask.state-message": "",
            "syntask.state-type": "RUNNING",
            "syntask.state-name": "Running",
            "syntask.state-timestamp": task_run_states[1].timestamp.isoformat(),
            "syntask.orchestration": "client",
        }
    )
    assert (
        pendulum.parse(running.payload["task_run"].pop("expected_start_time"))
        == task_run.expected_start_time
    )
    assert running.payload["task_run"].pop("task_key").startswith("happy_little_tree")
    assert (
        pendulum.parse(running.payload["task_run"].pop("start_time"))
        == task_run.start_time
    )
    assert running.payload == {
        "intended": {"from": "PENDING", "to": "RUNNING"},
        "initial_state": {
            "type": "PENDING",
            "name": "Pending",
            "message": "",
            "state_details": {},
        },
        "validated_state": {
            "type": "RUNNING",
            "name": "Running",
            "message": "",
            "state_details": {},
            "data": None,
        },
        "task_run": {
            "dynamic_key": task_run.dynamic_key,
            "empirical_policy": {
                "max_retries": 0,
                "retries": 0,
                "retry_delay": 0,
                "retry_delay_seconds": 0.0,
            },
            "flow_run_run_count": 1,
            "name": task_run.name,
            "run_count": 1,
            "tags": [],
            "task_inputs": {},
            "total_run_time": 0.0,
        },
    }

    assert completed.event == "syntask.task-run.Completed"
    assert completed.id == task_run_states[2].id
    assert completed.occurred == task_run_states[2].timestamp
    assert completed.resource == Resource(
        {
            "syntask.resource.id": f"syntask.task-run.{task_run.id}",
            "syntask.resource.name": task_run.name,
            "syntask.state-message": "",
            "syntask.state-type": "COMPLETED",
            "syntask.state-name": "Completed",
            "syntask.state-timestamp": task_run_states[2].timestamp.isoformat(),
            "syntask.orchestration": "client",
        }
    )
    assert (
        pendulum.parse(completed.payload["task_run"].pop("expected_start_time"))
        == task_run.expected_start_time
    )
    assert completed.payload["task_run"].pop("task_key").startswith("happy_little_tree")
    assert (
        pendulum.parse(completed.payload["task_run"].pop("start_time"))
        == task_run.start_time
    )
    assert (
        pendulum.parse(completed.payload["task_run"].pop("end_time"))
        == task_run.end_time
    )
    assert completed.payload["task_run"].pop("total_run_time") > 0.0
    assert completed.payload == {
        "intended": {"from": "RUNNING", "to": "COMPLETED"},
        "initial_state": {
            "type": "RUNNING",
            "name": "Running",
            "message": "",
            "state_details": {},
        },
        "validated_state": {
            "type": "COMPLETED",
            "name": "Completed",
            "message": "",
            "state_details": {},
            "data": None,
        },
        "task_run": {
            "dynamic_key": task_run.dynamic_key,
            "empirical_policy": {
                "max_retries": 0,
                "retries": 0,
                "retry_delay": 0,
                "retry_delay_seconds": 0.0,
            },
            "flow_run_run_count": 1,
            "name": task_run.name,
            "run_count": 1,
            "tags": [],
            "task_inputs": {},
        },
    }


async def test_task_state_change_task_failure(
    asserting_events_worker: EventsWorker,
    reset_worker_events,
    syntask_client,
    events_pipeline,
):
    @task
    def happy_little_tree():
        raise ValueError("Here's a happy little accident.")

    @flow
    def happy_path():
        return happy_little_tree(return_state=True)

    flow_state = happy_path(return_state=True)
    await events_pipeline.process_events(dequeue_events=False)

    task_state = await flow_state.result(raise_on_failure=False)
    task_run_id = task_state.state_details.task_run_id

    task_run = await syntask_client.read_task_run(task_run_id)
    task_run_states = await syntask_client.read_task_run_states(task_run_id)

    await asserting_events_worker.drain()
    assert isinstance(asserting_events_worker._client, AssertingEventsClient)
    events = [
        event
        for event in asserting_events_worker._client.events
        if event.event.startswith("syntask.task-run.")
    ]
    assert len(task_run_states) == len(events) == 3

    pending, running, failed = events

    assert pending.event == "syntask.task-run.Pending"
    assert pending.id == task_run_states[0].id
    assert pending.occurred == task_run_states[0].timestamp
    assert pending.resource == Resource(
        {
            "syntask.resource.id": f"syntask.task-run.{task_run.id}",
            "syntask.resource.name": task_run.name,
            "syntask.state-message": "",
            "syntask.state-type": "PENDING",
            "syntask.state-name": "Pending",
            "syntask.state-timestamp": task_run_states[0].timestamp.isoformat(),
            "syntask.orchestration": "client",
        }
    )
    assert (
        pendulum.parse(pending.payload["task_run"].pop("expected_start_time"))
        == task_run.expected_start_time
    )
    assert pending.payload["task_run"].pop("task_key").startswith("happy_little_tree")
    assert pending.payload == {
        "initial_state": None,
        "intended": {"from": None, "to": "PENDING"},
        "validated_state": {
            "type": "PENDING",
            "name": "Pending",
            "message": "",
            "state_details": {},
            "data": None,
        },
        "task_run": {
            "dynamic_key": task_run.dynamic_key,
            "empirical_policy": {
                "max_retries": 0,
                "retries": 0,
                "retry_delay": 0,
                "retry_delay_seconds": 0.0,
            },
            "flow_run_run_count": 0,
            "name": task_run.name,
            "run_count": 0,
            "tags": [],
            "task_inputs": {},
            "total_run_time": 0.0,
        },
    }

    assert running.event == "syntask.task-run.Running"
    assert running.id == task_run_states[1].id
    assert running.occurred == task_run_states[1].timestamp
    assert running.resource == Resource(
        {
            "syntask.resource.id": f"syntask.task-run.{task_run.id}",
            "syntask.resource.name": task_run.name,
            "syntask.state-message": "",
            "syntask.state-type": "RUNNING",
            "syntask.state-name": "Running",
            "syntask.state-timestamp": task_run_states[1].timestamp.isoformat(),
            "syntask.orchestration": "client",
        }
    )
    assert (
        pendulum.parse(running.payload["task_run"].pop("expected_start_time"))
        == task_run.expected_start_time
    )
    assert (
        pendulum.parse(running.payload["task_run"].pop("start_time"))
        == task_run.start_time
    )
    assert running.payload["task_run"].pop("task_key").startswith("happy_little_tree")
    assert running.payload == {
        "intended": {"from": "PENDING", "to": "RUNNING"},
        "initial_state": {
            "type": "PENDING",
            "name": "Pending",
            "message": "",
            "state_details": {},
        },
        "validated_state": {
            "type": "RUNNING",
            "name": "Running",
            "message": "",
            "state_details": {},
            "data": None,
        },
        "task_run": {
            "dynamic_key": task_run.dynamic_key,
            "empirical_policy": {
                "max_retries": 0,
                "retries": 0,
                "retry_delay": 0,
                "retry_delay_seconds": 0.0,
            },
            "flow_run_run_count": 1,
            "name": task_run.name,
            "run_count": 1,
            "tags": [],
            "task_inputs": {},
            "total_run_time": 0.0,
        },
    }

    assert failed.event == "syntask.task-run.Failed"
    assert failed.id == task_run_states[2].id
    assert failed.occurred == task_run_states[2].timestamp
    assert failed.resource == Resource(
        {
            "syntask.resource.id": f"syntask.task-run.{task_run.id}",
            "syntask.resource.name": task_run.name,
            "syntask.state-message": (
                "Task run encountered an exception ValueError: "
                "Here's a happy little accident."
            ),
            "syntask.state-type": "FAILED",
            "syntask.state-name": "Failed",
            "syntask.state-timestamp": task_run_states[2].timestamp.isoformat(),
            "syntask.orchestration": "client",
        }
    )
    assert (
        pendulum.parse(failed.payload["task_run"].pop("expected_start_time"))
        == task_run.expected_start_time
    )
    assert failed.payload["task_run"].pop("task_key").startswith("happy_little_tree")
    assert (
        pendulum.parse(failed.payload["task_run"].pop("start_time"))
        == task_run.start_time
    )
    assert (
        pendulum.parse(failed.payload["task_run"].pop("end_time")) == task_run.end_time
    )
    assert failed.payload["task_run"].pop("total_run_time") > 0
    assert failed.payload == {
        "intended": {"from": "RUNNING", "to": "FAILED"},
        "initial_state": {
            "type": "RUNNING",
            "name": "Running",
            "message": "",
            "state_details": {},
        },
        "validated_state": {
            "type": "FAILED",
            "name": "Failed",
            "message": (
                "Task run encountered an exception ValueError: "
                "Here's a happy little accident."
            ),
            "state_details": {"retriable": False},
            "data": None,
        },
        "task_run": {
            "dynamic_key": task_run.dynamic_key,
            "empirical_policy": {
                "max_retries": 0,
                "retries": 0,
                "retry_delay": 0,
                "retry_delay_seconds": 0.0,
            },
            "flow_run_run_count": 1,
            "name": task_run.name,
            "run_count": 1,
            "tags": [],
            "task_inputs": {},
        },
    }


async def test_background_task_state_changes(
    asserting_events_worker: EventsWorker,
    reset_worker_events,
    syntask_client,
    tmp_path,
    events_pipeline,
):
    storage = LocalFileSystem(basepath=tmp_path)
    await storage.save("test")

    @task(result_storage=storage)
    def foo():
        pass

    task_run_future = foo.apply_async()
    task_run = await syntask_client.read_task_run(task_run_future.task_run_id)

    await TaskWorker(foo).execute_task_run(task_run)
    await events_pipeline.process_events(dequeue_events=False)

    task_run_states = await syntask_client.read_task_run_states(
        task_run_future.task_run_id
    )

    await asserting_events_worker.drain()

    events = sorted(asserting_events_worker._client.events, key=lambda e: e.occurred)
    events = [e for e in events if e.event.startswith("syntask.task-run.")]

    assert len(task_run_states) == len(events) == 4

    assert [e.event for e in events] == [
        "syntask.task-run.Scheduled",
        "syntask.task-run.Pending",
        "syntask.task-run.Running",
        "syntask.task-run.Completed",
    ]

    observed = [
        (e.payload["intended"]["from"], e.payload["intended"]["to"])
        for e in events
        if e.event.startswith("syntask.task-run.")
    ]
    expected = [
        (None, "SCHEDULED"),
        ("SCHEDULED", "PENDING"),
        ("PENDING", "RUNNING"),
        ("RUNNING", "COMPLETED"),
    ]
    assert observed == expected


async def test_apply_async_emits_scheduled_event(
    asserting_events_worker,
    syntask_client,
):
    @task
    def happy_little_tree():
        return "🌳"

    future = happy_little_tree.apply_async()
    task_run_id = future.task_run_id

    await asserting_events_worker.drain()

    events = asserting_events_worker._client.events
    assert len(events) == 1
    scheduled = events[0]

    task_run = await syntask_client.read_task_run(task_run_id)
    assert task_run
    assert task_run.id == task_run_id
    task_run_states = await syntask_client.read_task_run_states(task_run_id)
    assert len(task_run_states) == 1

    assert scheduled.event == "syntask.task-run.Scheduled"
    assert scheduled.id == task_run_states[0].id
    assert scheduled.occurred == task_run_states[0].timestamp
    assert scheduled.resource == Resource(
        {
            "syntask.resource.id": f"syntask.task-run.{task_run_id}",
            "syntask.resource.name": task_run.name,
            "syntask.state-message": "",
            "syntask.state-type": "SCHEDULED",
            "syntask.state-name": "Scheduled",
            "syntask.state-timestamp": task_run_states[0].timestamp.isoformat(),
            "syntask.orchestration": "client",
        }
    )

    assert (
        pendulum.parse(
            scheduled.payload["validated_state"]["state_details"].pop("scheduled_time")
        )
        == task_run.expected_start_time
    )
    assert (
        pendulum.parse(scheduled.payload["task_run"].pop("next_scheduled_start_time"))
        == task_run.next_scheduled_start_time
    )
    assert (
        pendulum.parse(scheduled.payload["task_run"].pop("expected_start_time"))
        == task_run.expected_start_time
    )

    assert scheduled.payload["task_run"].pop("name").startswith("happy_little_tree")
    assert (
        scheduled.payload["task_run"].pop("dynamic_key").startswith("happy_little_tree")
    )
    assert scheduled.payload["task_run"].pop("task_key").startswith("happy_little_tree")
    assert scheduled.payload == {
        "initial_state": None,
        "intended": {"from": None, "to": "SCHEDULED"},
        "validated_state": {
            "type": "SCHEDULED",
            "name": "Scheduled",
            "message": "",
            "state_details": {
                "pause_reschedule": False,
                "untrackable_result": False,
                "deferred": True,
            },
            "data": None,
        },
        "task_run": {
            "empirical_policy": {
                "max_retries": 0,
                "retries": 0,
                "retry_delay": 0,
                "retry_delay_seconds": 0.0,
            },
            "flow_run_run_count": 0,
            "run_count": 0,
            "tags": [],
            "task_inputs": {},
            "total_run_time": 0.0,
        },
    }
