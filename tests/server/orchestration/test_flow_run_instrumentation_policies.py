from contextlib import AsyncExitStack
from datetime import timedelta
from typing import Any, Dict
from unittest import mock
from uuid import uuid4

import httpx
import pendulum
import pytest
from fastapi.applications import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from syntask import states as client_states
from syntask.server import models
from syntask.server.database.orm_models import (
    ORMDeployment,
    ORMFlow,
    ORMFlowRun,
    ORMTaskRun,
    ORMWorkPool,
    ORMWorkQueue,
)
from syntask.server.events.clients import AssertingEventsClient
from syntask.server.events.schemas.events import RelatedResource, Resource
from syntask.server.models import events, flow_run_states, flow_runs, workers
from syntask.server.models.events import _flow_run_resource_data_cache
from syntask.server.models.work_queues import create_work_queue
from syntask.server.orchestration.instrumentation_policies import (
    InstrumentFlowRunStateTransitions,
)
from syntask.server.orchestration.rules import (
    ALL_ORCHESTRATION_STATES,
    BaseOrchestrationRule,
    FlowOrchestrationContext,
    TaskOrchestrationContext,
)
from syntask.server.schemas.actions import WorkQueueCreate
from syntask.server.schemas.core import CreatedBy, FlowRun
from syntask.server.schemas.responses import FlowRunResponse
from syntask.server.schemas.states import (
    Pending,
    State,
    StateDetails,
    StateType,
)


@pytest.fixture(autouse=True)
def cleared_resource_data_cache():
    _flow_run_resource_data_cache.clear()


@pytest.fixture
async def orchestration_parameters() -> Dict[str, Any]:
    return {}


async def test_instrumenting_a_flow_run_state_change(
    session: AsyncSession,
    flow: ORMFlow,
    flow_run: ORMFlowRun,
    start_of_test: pendulum.DateTime,
    orchestration_parameters: Dict[str, Any],
):
    transition = (StateType.PENDING, StateType.RUNNING)
    context = FlowOrchestrationContext(
        initial_state=State(type=transition[0]),
        proposed_state=State(type=transition[1]),
        run=flow_run,
        session=session,
        parameters=orchestration_parameters,
    )

    async with InstrumentFlowRunStateTransitions(context, *transition):
        await context.validate_proposed_state()
    await session.commit()

    assert AssertingEventsClient.last
    (event,) = AssertingEventsClient.last.events

    assert context.proposed_state
    assert event.event == "syntask.flow-run.Running"
    assert start_of_test <= event.occurred <= pendulum.now("UTC")

    assert event.resource == Resource.model_validate(
        {
            "syntask.resource.id": f"syntask.flow-run.{flow_run.id}",
            "syntask.resource.name": flow_run.name,
            "syntask.state-message": "",
            "syntask.state-name": "Running",
            "syntask.state-timestamp": context.proposed_state.timestamp.isoformat(),
            "syntask.state-type": "RUNNING",
        }
    )
    assert event.related == [
        RelatedResource.model_validate(
            {
                "syntask.resource.id": f"syntask.flow.{flow.id}",
                "syntask.resource.role": "flow",
                "syntask.resource.name": "my-flow",
            }
        )
    ]


@pytest.mark.parametrize(
    "created_by, resource_prefix",
    [
        (
            CreatedBy(id=uuid4(), type="DEPLOYMENT", display_value="Deployjoy"),
            "syntask.deployment",
        ),
        (
            CreatedBy(id=uuid4(), type="AUTOMATION", display_value="I'm Triggered"),
            "syntask.automation",
        ),
        (
            CreatedBy(id=uuid4(), type="NEVERHOIDOFIT", display_value="anything"),
            None,
        ),
    ],
)
async def test_capturing_flow_run_provenance_as_related_resource(
    session: AsyncSession,
    flow: ORMFlow,
    flow_run: ORMFlowRun,
    start_of_test: pendulum.DateTime,
    orchestration_parameters: Dict[str, Any],
    created_by: CreatedBy,
    resource_prefix: str,
):
    flow_run.created_by = created_by
    session.add(flow_run)
    await session.commit()

    transition = (StateType.PENDING, StateType.RUNNING)
    context = FlowOrchestrationContext(
        initial_state=State(type=transition[0]),
        proposed_state=State(type=transition[1]),
        run=flow_run,
        session=session,
        parameters=orchestration_parameters,
    )

    async with InstrumentFlowRunStateTransitions(context, *transition):
        await context.validate_proposed_state()
    await session.commit()

    assert AssertingEventsClient.last
    (event,) = AssertingEventsClient.last.events

    creators = [r for r in event.related if r.role == "creator"]
    if resource_prefix is None:
        assert not creators
    else:
        assert creators == [
            RelatedResource.model_validate(
                {
                    "syntask.resource.id": f"{resource_prefix}.{created_by.id}",
                    "syntask.resource.role": "creator",
                    "syntask.resource.name": created_by.display_value,
                }
            )
        ]


async def test_flow_run_state_change_events_capture_order_on_short_gaps(
    session: AsyncSession,
    flow: ORMFlow,
    flow_run: ORMFlowRun,
    start_of_test: pendulum.DateTime,
    orchestration_parameters: Dict[str, Any],
):
    # send the pending state through orchestration so it is written to the DB
    pending_state: State = State(
        type=StateType.PENDING,
        timestamp=start_of_test - timedelta(minutes=2),
    )
    pending_transition = (None, StateType.PENDING)
    context = FlowOrchestrationContext(
        initial_state=None,
        proposed_state=pending_state,
        run=flow_run,
        session=session,
        parameters=orchestration_parameters,
    )

    async with InstrumentFlowRunStateTransitions(context, *pending_transition):
        await context.validate_proposed_state()
    await session.commit()

    from_db = await flow_run_states.read_flow_run_state(session, pending_state.id)
    assert from_db
    pending_state = State.model_validate(from_db, from_attributes=True)

    # Now process the Pending->Running transition and confirm it sends an event
    running_state: State = State(type=StateType.RUNNING)
    running_transition = (pending_state.type, running_state.type)
    context = FlowOrchestrationContext(
        initial_state=pending_state,
        proposed_state=running_state,
        run=flow_run,
        session=session,
        parameters=orchestration_parameters,
    )
    async with InstrumentFlowRunStateTransitions(context, *running_transition):
        await context.validate_proposed_state()
    await session.commit()

    assert len(AssertingEventsClient.all) == 2
    all_events = {e.events[0].event for e in AssertingEventsClient.all}
    assert all_events == {"syntask.flow-run.Pending", "syntask.flow-run.Running"}

    assert AssertingEventsClient.last
    (event,) = AssertingEventsClient.last.events

    assert event.event == "syntask.flow-run.Running"
    assert event.id == running_state.id

    # we _do_ track event.follows here because the events are close enough in time
    # that we might need to disambiguate the ordering of them in downstream systems
    assert event.follows == pending_state.id


async def test_flow_run_state_change_events_do_not_capture_order_on_long_gaps(
    session: AsyncSession,
    flow: ORMFlow,
    flow_run: ORMFlowRun,
    start_of_test: pendulum.DateTime,
    orchestration_parameters: Dict[str, Any],
):
    # send the pending state through orchestration so it is written to the DB
    pending_state: State = State(
        type=StateType.PENDING,
        timestamp=start_of_test - timedelta(minutes=15),
    )
    pending_transition = (None, StateType.PENDING)
    context = FlowOrchestrationContext(
        initial_state=None,
        proposed_state=pending_state,
        run=flow_run,
        session=session,
        parameters=orchestration_parameters,
    )

    async with InstrumentFlowRunStateTransitions(context, *pending_transition):
        await context.validate_proposed_state()
    await session.commit()

    from_db = await flow_run_states.read_flow_run_state(session, pending_state.id)
    assert from_db
    pending_state = State.model_validate(from_db, from_attributes=True)

    # Now process the Pending->Running transition and confirm it sends an event
    running_state: State = State(type=StateType.RUNNING)
    running_transition = (pending_state.type, running_state.type)
    context = FlowOrchestrationContext(
        initial_state=pending_state,
        proposed_state=running_state,
        run=flow_run,
        session=session,
        parameters=orchestration_parameters,
    )
    async with InstrumentFlowRunStateTransitions(context, *running_transition):
        await context.validate_proposed_state()
    await session.commit()

    assert AssertingEventsClient.last
    (event,) = AssertingEventsClient.last.events

    assert event.event == "syntask.flow-run.Running"
    assert event.id == running_state.id

    # we _do not_ track event.follows here because the events are distant enough in time
    # that we don't need to ensure their local ordering
    assert event.follows is None


async def test_flow_run_state_change_events_do_not_capture_order_on_initial_transition(
    session: AsyncSession,
    flow: ORMFlow,
    flow_run: ORMFlowRun,
    start_of_test: pendulum.DateTime,
    orchestration_parameters: Dict[str, Any],
):
    pending_state: State = State(type=StateType.PENDING)
    transition = (None, StateType.PENDING)
    context = FlowOrchestrationContext(
        initial_state=None,
        proposed_state=pending_state,
        run=flow_run,
        session=session,
        parameters=orchestration_parameters,
    )

    async with InstrumentFlowRunStateTransitions(context, *transition):
        await context.validate_proposed_state()
    await session.commit()

    assert AssertingEventsClient.last
    (event,) = AssertingEventsClient.last.events

    assert event.event == "syntask.flow-run.Pending"
    assert event.id == pending_state.id
    assert event.follows is None


async def test_instrumenting_a_flow_run_with_no_flow(
    session: AsyncSession,
    flow: ORMFlow,
    flow_run: ORMFlowRun,
    start_of_test: pendulum.DateTime,
    orchestration_parameters: Dict[str, Any],
):
    """Regression test for errors observed on 2023-02-01, where a flow run was found
    but the associated flow was not.  Likely due to a race condition at the point of
    emitting the event.  We can emit a barebones version of the event without the
    typical related resources."""
    transition = (StateType.PENDING, StateType.RUNNING)
    context = FlowOrchestrationContext(
        initial_state=State(type=transition[0]),
        proposed_state=State(type=transition[1]),
        run=flow_run,
        session=session,
        parameters=orchestration_parameters,
    )

    # emulate the race condition where a flow is deleted just after getting a flow_run
    with mock.patch(
        "syntask.server.models.events.models.flows.read_flow",
        return_value=None,
        spec=models.flows.read_flow,
    ):
        async with InstrumentFlowRunStateTransitions(context, *transition):
            await context.validate_proposed_state()
        await session.commit()

    assert AssertingEventsClient.last
    (event,) = AssertingEventsClient.last.events

    assert context.proposed_state
    assert event.event == "syntask.flow-run.Running"
    assert start_of_test <= event.occurred <= pendulum.now("UTC")

    assert event.resource == Resource.model_validate(
        {
            "syntask.resource.id": f"syntask.flow-run.{flow_run.id}",
            "syntask.resource.name": flow_run.name,
            "syntask.state-message": "",
            "syntask.state-name": "Running",
            "syntask.state-timestamp": context.proposed_state.timestamp.isoformat(),
            "syntask.state-type": "RUNNING",
        }
    )
    # flow runs without a flow won't be able to have any related resources
    assert event.related == []


async def test_instrumenting_a_flow_run_includes_state_in_payload(
    session: AsyncSession,
    flow_run,
    orchestration_parameters: Dict[str, Any],
):
    transition = (None, StateType.RUNNING)
    context = FlowOrchestrationContext(
        initial_state=None,
        proposed_state=State(type=transition[1], name="custom", message="foo"),
        run=flow_run,
        session=session,
        parameters=orchestration_parameters,
    )

    async with InstrumentFlowRunStateTransitions(context, *transition):
        await context.validate_proposed_state()
    await session.commit()

    assert AssertingEventsClient.last
    (event,) = AssertingEventsClient.last.events

    assert event.payload == {
        "intended": {"from": None, "to": "RUNNING"},
        "initial_state": None,
        "validated_state": {"type": "RUNNING", "name": "custom", "message": "foo"},
    }


async def test_instrumenting_a_deployed_flow_run_state_change(
    session: AsyncSession,
    flow: ORMFlow,
    deployment: ORMDeployment,
    flow_run: ORMFlowRun,
    orchestration_parameters: Dict[str, Any],
):
    flow_run.deployment_id = deployment.id
    session.add(flow_run)
    await session.commit()

    transition = (StateType.PENDING, StateType.RUNNING)
    context = FlowOrchestrationContext(
        initial_state=State(type=transition[0]),
        proposed_state=State(type=transition[1]),
        run=flow_run,
        session=session,
        parameters=orchestration_parameters,
    )

    async with InstrumentFlowRunStateTransitions(context, *transition):
        await context.validate_proposed_state()
    await session.commit()

    assert AssertingEventsClient.last
    (event,) = AssertingEventsClient.last.events

    assert event.related == [
        RelatedResource.model_validate(
            {
                "syntask.resource.id": f"syntask.flow.{flow.id}",
                "syntask.resource.role": "flow",
                "syntask.resource.name": "my-flow",
            }
        ),
        RelatedResource.model_validate(
            {
                "syntask.resource.id": f"syntask.deployment.{deployment.id}",
                "syntask.resource.role": "deployment",
                "syntask.resource.name": deployment.name,
            }
        ),
        RelatedResource.model_validate(
            {
                "syntask.resource.id": "syntask.tag.test",
                "syntask.resource.role": "tag",
            }
        ),
    ]


async def test_instrumenting_a_flow_with_tags(
    session: AsyncSession,
    flow: ORMFlow,
    deployment: ORMDeployment,
    flow_run: ORMFlowRun,
    start_of_test: pendulum.DateTime,
    orchestration_parameters: Dict[str, Any],
):
    flow_run.tags = ["flow-run-one"]
    flow.tags = ["flow-one", "common-one"]
    deployment.tags = ["deployment-one", "common-one"]
    flow_run.deployment_id = deployment.id
    session.add_all(
        [
            flow_run,
            flow,
            deployment,
            flow_run,
        ]
    )
    await session.commit()

    transition = (StateType.PENDING, StateType.RUNNING)
    context = FlowOrchestrationContext(
        initial_state=State(type=transition[0]),
        proposed_state=State(type=transition[1]),
        run=flow_run,
        session=session,
        parameters=orchestration_parameters,
    )

    async with InstrumentFlowRunStateTransitions(context, *transition):
        await context.validate_proposed_state()
    await session.commit()

    assert AssertingEventsClient.last
    (event,) = AssertingEventsClient.last.events

    assert len(event.related) == 6  # two of these are the flow and deployment

    assert (
        RelatedResource.model_validate(
            {
                "syntask.resource.id": "syntask.tag.common-one",
                "syntask.resource.role": "tag",
            }
        )
        in event.related
    )
    assert (
        RelatedResource.model_validate(
            {
                "syntask.resource.id": "syntask.tag.deployment-one",
                "syntask.resource.role": "tag",
            }
        )
        in event.related
    )
    assert (
        RelatedResource.model_validate(
            {
                "syntask.resource.id": "syntask.tag.flow-run-one",
                "syntask.resource.role": "tag",
            }
        )
        in event.related
    )
    assert (
        RelatedResource.model_validate(
            {
                "syntask.resource.id": "syntask.tag.flow-one",
                "syntask.resource.role": "tag",
            }
        )
        in event.related
    )


@pytest.fixture
async def work_queue(session: AsyncSession):
    work_queue = await create_work_queue(
        session=session,
        work_queue=WorkQueueCreate(name="This is a queuey one"),
    )
    await session.commit()

    return work_queue


@pytest.fixture
async def work_pool(session: AsyncSession, work_queue: ORMWorkQueue):
    work_pool = await workers.read_work_pool(
        session=session,
        work_pool_id=work_queue.work_pool_id,
    )

    return work_pool


async def test_instrumenting_a_flow_run_from_a_work_queue(
    session: AsyncSession,
    flow,
    work_queue,
    work_pool,
    flow_run,
    start_of_test: pendulum.DateTime,
    orchestration_parameters: Dict[str, Any],
):
    flow_run.work_queue_id = work_queue.id
    session.add(flow_run)
    await session.commit()

    transition = (StateType.PENDING, StateType.RUNNING)
    context = FlowOrchestrationContext(
        initial_state=State(type=transition[0]),
        proposed_state=State(type=transition[1]),
        run=flow_run,
        session=session,
        parameters=orchestration_parameters,
    )

    async with InstrumentFlowRunStateTransitions(context, *transition):
        await context.validate_proposed_state()
    await session.commit()

    assert AssertingEventsClient.last
    (event,) = AssertingEventsClient.last.events

    assert len(event.related) == 3  # the other one is the flow

    assert (
        RelatedResource.model_validate(
            {
                "syntask.resource.id": f"syntask.work-queue.{work_queue.id}",
                "syntask.resource.role": "work-queue",
                "syntask.resource.name": "This is a queuey one",
            }
        )
        in event.related
    )

    assert (
        RelatedResource.model_validate(
            {
                "syntask.resource.id": f"syntask.work-pool.{work_pool.id}",
                "syntask.resource.role": "work-pool",
                "syntask.resource.name": work_pool.name,
            }
        )
        in event.related
    )


async def test_does_nothing_for_task_transitions(
    session: AsyncSession,
    task_run: ORMTaskRun,
    orchestration_parameters: Dict[str, Any],
):
    transition = (StateType.PENDING, StateType.RUNNING)
    context = TaskOrchestrationContext(
        initial_state=State(type=transition[0]),
        proposed_state=State(type=transition[1]),
        run=task_run,
        session=session,
    )

    async with InstrumentFlowRunStateTransitions(context, *transition):
        await context.validate_proposed_state()
    await session.commit()

    # no events should have been emitted
    assert not AssertingEventsClient.last


async def test_still_instruments_rejected_state_transitions(
    session: AsyncSession,
    flow_run: ORMFlowRun,
    orchestration_parameters: Dict[str, Any],
):
    transition = (StateType.PENDING, StateType.RUNNING)
    context = FlowOrchestrationContext(
        initial_state=State(type=transition[0]),
        proposed_state=State(type=transition[1]),
        run=flow_run,
        session=session,
        parameters=orchestration_parameters,
    )

    class FussyRule(BaseOrchestrationRule):
        FROM_STATES = ALL_ORCHESTRATION_STATES
        TO_STATES = ALL_ORCHESTRATION_STATES

        async def before_transition(self, initial_state, proposed_state, context):
            new_state = proposed_state.model_copy()
            new_state.name = "Cancelled Fussily"
            new_state.type = StateType.CANCELLED
            await self.reject_transition(new_state, reason="I am fussy")

        async def after_transition(self, initial_state, validated_state, context):
            pass

        async def cleanup(self, initial_state, validated_state, context):
            pass

    fussy_policy = [
        InstrumentFlowRunStateTransitions,
        FussyRule,
    ]

    async with AsyncExitStack() as stack:
        for rule in fussy_policy:
            context = await stack.enter_async_context(rule(context, *transition))
        await context.validate_proposed_state()
    await session.commit()

    # The validated transition should be emitted

    assert AssertingEventsClient.last
    (event,) = AssertingEventsClient.last.events

    assert event.event == "syntask.flow-run.Cancelled Fussily"
    assert event.resource["syntask.state-type"] == "CANCELLED"


async def test_does_nothing_for_aborted_transitions(
    session: AsyncSession,
    flow_run,
    orchestration_parameters: Dict[str, Any],
):
    transition = (StateType.PENDING, StateType.RUNNING)
    context = FlowOrchestrationContext(
        initial_state=State(type=transition[0]),
        proposed_state=State(type=transition[1]),
        run=flow_run,
        session=session,
        parameters=orchestration_parameters,
    )

    class UglyRule(BaseOrchestrationRule):
        FROM_STATES = ALL_ORCHESTRATION_STATES
        TO_STATES = ALL_ORCHESTRATION_STATES

        async def before_transition(self, initial_state, proposed_state, context):
            await self.abort_transition("I am just plain ugly")

        async def after_transition(self, initial_state, validated_state, context):
            pass

        async def cleanup(self, initial_state, validated_state, context):
            pass

    ugly_policy = [
        InstrumentFlowRunStateTransitions,
        UglyRule,
    ]

    async with AsyncExitStack() as stack:
        for rule in ugly_policy:
            context = await stack.enter_async_context(rule(context, *transition))
        await context.validate_proposed_state()
    await session.commit()

    # no events should have been emitted
    assert not AssertingEventsClient.last


async def test_does_nothing_for_delayed_transitions(
    session: AsyncSession,
    flow_run,
    orchestration_parameters: Dict[str, Any],
):
    transition = (StateType.PENDING, StateType.RUNNING)
    context = FlowOrchestrationContext(
        initial_state=State(type=transition[0]),
        proposed_state=State(type=transition[1]),
        run=flow_run,
        session=session,
        parameters=orchestration_parameters,
    )

    class ProcrastinatingRule(BaseOrchestrationRule):
        FROM_STATES = ALL_ORCHESTRATION_STATES
        TO_STATES = ALL_ORCHESTRATION_STATES

        async def before_transition(self, initial_state, proposed_state, context):
            await self.delay_transition(10, "I'll get to it when I get to it")

        async def after_transition(self, initial_state, validated_state, context):
            pass

        async def cleanup(self, initial_state, validated_state, context):
            pass

    Procrastinating_policy = [
        InstrumentFlowRunStateTransitions,
        ProcrastinatingRule,
    ]

    async with AsyncExitStack() as stack:
        for rule in Procrastinating_policy:
            context = await stack.enter_async_context(rule(context, *transition))
        await context.validate_proposed_state()
    await session.commit()

    # no events should have been emitted
    assert not AssertingEventsClient.last


@pytest.fixture
async def client(app: FastAPI):
    # The automations tests assume that the client will not raise exceptions and will
    # serve any server-side errors as HTTP responses.  This is different than some other
    # parts of the general test suite, so we'll override the fixture here.

    transport = ASGITransport(app=app, raise_app_exceptions=False)

    async with httpx.AsyncClient(
        transport=transport, base_url="https://test/api"
    ) as async_client:
        yield async_client


async def test_cancelling_to_cancelled_transitions(
    session: AsyncSession,
    client: AsyncClient,
    flow_run: ORMFlowRun,
    start_of_test: pendulum.DateTime,
):
    """Regression test for https://github.com/SynoPKG/nebula/issues/2826, where
    we observed that flow runs firing Cancelling events never end up firing Cancelled
    events.  Uses the API for a more realistic reproduction case."""
    await flow_runs.set_flow_run_state(
        session=session,
        flow_run_id=flow_run.id,
        state=State(type=StateType.CANCELLED, name="Cancelling"),
    )
    await session.commit()

    response = await client.post(
        f"flow_runs/{flow_run.id}/set_state",
        json={
            "state": client_states.Cancelled()
            .to_state_create()
            .model_dump(mode="json"),
            "force": True,  # the Agent uses force=True here, which caused the bug
        },
    )
    assert response.status_code == 201, response.text

    response = await client.get(
        f"/flow_runs/{flow_run.id}",
    )
    assert response.status_code == 200

    updated_flow_run = FlowRunResponse.model_validate(response.json())
    assert updated_flow_run.state

    assert AssertingEventsClient.last
    (event,) = AssertingEventsClient.last.events

    assert event.event == "syntask.flow-run.Cancelled"
    assert start_of_test <= event.occurred <= pendulum.now("UTC")

    assert event.resource == Resource.model_validate(
        {
            "syntask.resource.id": f"syntask.flow-run.{flow_run.id}",
            "syntask.resource.name": flow_run.name,
            "syntask.state-message": "",
            "syntask.state-name": "Cancelled",
            "syntask.state-timestamp": updated_flow_run.state.timestamp.isoformat(),
            "syntask.state-type": "CANCELLED",
        }
    )


async def test_caches_resource_data(
    session: AsyncSession,
    work_queue,
    work_pool,
    flow: ORMFlow,
    flow_run: ORMFlowRun,
    deployment: ORMDeployment,
    orchestration_parameters: Dict[str, Any],
):
    flow_run.work_queue_id = work_queue.id
    flow_run.tags = ["flow-run-one", "common-one"]
    flow.tags = ["flow-one", "common-one"]
    deployment.tags = ["deployment-one", "common-one"]
    flow_run.deployment_id = deployment.id
    session.add_all(
        [
            flow,
            deployment,
            flow_run,
        ]
    )

    transition = (StateType.PENDING, StateType.RUNNING)
    context = FlowOrchestrationContext(
        initial_state=State(type=transition[0]),
        proposed_state=State(type=transition[1]),
        run=flow_run,
        session=session,
        parameters=orchestration_parameters,
    )

    async with InstrumentFlowRunStateTransitions(context, *transition):
        await context.validate_proposed_state()
    await session.commit()

    assert AssertingEventsClient.last

    related = _flow_run_resource_data_cache[flow_run.id]

    assert related == {
        "flow-run": {
            "id": str(flow_run.id),
            "name": flow_run.name,
            "tags": ["flow-run-one", "common-one"],
            "role": "flow-run",
        },
        "flow": {
            "id": str(flow.id),
            "name": flow.name,
            "tags": ["flow-one", "common-one"],
            "role": "flow",
        },
        "deployment": {
            "id": str(deployment.id),
            "name": deployment.name,
            "tags": ["deployment-one", "common-one"],
            "role": "deployment",
        },
        "work-queue": {
            "id": str(work_queue.id),
            "name": work_queue.name,
            "tags": [],
            "role": "work-queue",
        },
        "work-pool": {
            "id": str(work_pool.id),
            "name": work_pool.name,
            "tags": [],
            "role": "work-pool",
        },
        "task-run": {},
    }


async def test_caches_resource_data_for_subflow_runs(
    session: AsyncSession,
    work_queue: ORMWorkQueue,
    work_pool: ORMWorkPool,
    task_run: ORMTaskRun,
    flow: ORMFlow,
    orchestration_parameters: Dict[str, Any],
):
    task_run.tags = ["task-run-one", "common-one"]
    await session.commit()

    flow_run = await flow_runs.create_flow_run(
        session=session,
        flow_run=FlowRun(
            flow_id=flow.id,
            flow_version="1.0",
            state=Pending(),
            job_variables={"x": "y"},
            parent_task_run_id=task_run.id,
            work_queue_id=work_queue.id,
            tags=["flow-run-one", "common-one"],
        ),
    )

    session.add_all(
        [
            flow_run,
            task_run,
        ]
    )
    await session.commit()

    transition = (StateType.PENDING, StateType.RUNNING)
    context = FlowOrchestrationContext(
        initial_state=State(type=transition[0]),
        proposed_state=State(type=transition[1]),
        run=flow_run,
        session=session,
        parameters=orchestration_parameters,
    )

    async with InstrumentFlowRunStateTransitions(context, *transition):
        await context.validate_proposed_state()

    await session.commit()

    assert AssertingEventsClient.last

    related = _flow_run_resource_data_cache[flow_run.id]

    assert related == {
        "flow-run": {
            "id": str(flow_run.id),
            "name": flow_run.name,
            "tags": ["flow-run-one", "common-one"],
            "role": "flow-run",
        },
        "deployment": {},
        "flow": {
            "id": str(flow.id),
            "name": flow.name,
            "tags": [],
            "role": "flow",
        },
        "work-queue": {
            "id": str(work_queue.id),
            "name": work_queue.name,
            "tags": [],
            "role": "work-queue",
        },
        "work-pool": {
            "id": str(work_pool.id),
            "name": work_pool.name,
            "tags": [],
            "role": "work-pool",
        },
        "task-run": {
            "id": str(task_run.id),
            "name": task_run.name,
            "tags": ["task-run-one", "common-one"],
            "role": "task-run",
        },
    }


@pytest.fixture
def odd_truncation(monkeypatch: pytest.MonkeyPatch):
    assert 50_000 < events.TRUNCATE_STATE_MESSAGES_AT < 1_000_000
    monkeypatch.setattr(events, "TRUNCATE_STATE_MESSAGES_AT", 11)


@pytest.mark.parametrize(
    "message, expected",
    [
        (None, None),
        ("", None),
        ("a", "a"),
        ("heyyy", "heyyy"),
        ("12345678901", "12345678901"),
        ("123456789012", "123456789012"),  # because let's not be silly
        (
            "12345xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxghijk",
            "12345...39 additional characters...ghijk",
        ),
        (
            "12345xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxghijk",
            "12345...40 additional characters...ghijk",
        ),
    ],
)
def test_truncating_state_messages_at_odd_length(
    odd_truncation: None,
    message: str,
    expected: str,
):
    payload = events.state_payload(
        State(
            type=StateType.PENDING,
            name="Pending",
            message=message,
        )
    )
    assert payload
    assert payload.get("message") == expected


@pytest.fixture
def even_truncation(monkeypatch: pytest.MonkeyPatch):
    assert 50_000 < events.TRUNCATE_STATE_MESSAGES_AT < 1_000_000
    monkeypatch.setattr(events, "TRUNCATE_STATE_MESSAGES_AT", 10)


@pytest.mark.parametrize(
    "message, expected",
    [
        (None, None),
        ("", None),
        ("a", "a"),
        ("heyyy", "heyyy"),
        ("12345678901", "12345678901"),
        ("123456789012", "123456789012"),  # because let's not be silly
        (
            "12345xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxghijk",
            "12345...39 additional characters...ghijk",
        ),
        (
            "12345xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxghijk",
            "12345...40 additional characters...ghijk",
        ),
    ],
)
def test_truncating_state_messages_at_even_length(
    even_truncation: None,
    message: str,
    expected: str,
):
    payload = events.state_payload(
        State(
            type=StateType.PENDING,
            name="Pending",
            message=message,
        )
    )
    assert payload
    assert payload.get("message") == expected


def test_state_payload_paused_state():
    payload = events.state_payload(
        State(
            type=StateType.PAUSED,
            name="Paused",
            state_details=StateDetails(pause_reschedule=True),
        )
    )
    assert payload
    assert payload["pause_reschedule"] == "true"
