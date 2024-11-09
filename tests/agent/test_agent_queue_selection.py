import random

import syntask.exceptions
from syntask.agent import SyntaskAgent
from syntask.client.orchestration import SyntaskClient
from syntask.client.schemas.actions import WorkPoolCreate
from syntask.client.schemas.objects import WorkPool
from syntask.server.models.workers import DEFAULT_AGENT_WORK_POOL_NAME


async def _safe_get_or_create_workpool(
    client: SyntaskClient, *, name: str, type=str
) -> WorkPool:
    try:
        pool = await client.create_work_pool(WorkPoolCreate(name=name, type=type))
    except syntask.exceptions.ObjectAlreadyExists:
        pool = await client.read_work_pool(name)
    return pool


async def test_get_work_queues_returns_default_queues(syntask_client: SyntaskClient):
    # create WorkPools to associate with our WorkQueues
    default = await _safe_get_or_create_workpool(
        syntask_client, name=DEFAULT_AGENT_WORK_POOL_NAME, type="syntask-agent"
    )
    ecs = await _safe_get_or_create_workpool(syntask_client, name="ecs", type="ecs")
    agent_pool = await _safe_get_or_create_workpool(
        syntask_client, name="agent", type="syntask-agent"
    )

    # create WorkQueues, associating them with a pool at random
    expected = set()
    for i in range(10):
        random_pool = random.choice([default, ecs, agent_pool])
        q = await syntask_client.create_work_queue(
            name="test-{i}".format(i=i), work_pool_name=random_pool.name
        )
        if random_pool == default:
            expected.add(q.name)

    # create an agent with a prefix that matches all of the created queues
    async with SyntaskAgent(work_queue_prefix=["test-"]) as agent:
        results = {q.name async for q in agent.get_work_queues()}

    # verify that only WorkQueues with in the default pool are returned for
    # this agent since it does not have a work pool name
    assert results == expected
