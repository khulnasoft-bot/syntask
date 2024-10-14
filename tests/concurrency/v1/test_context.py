import asyncio
import time
from uuid import UUID

import pytest

from syntask.client.orchestration import SyntaskClient, get_client
from syntask.concurrency.v1.asyncio import concurrency as aconcurrency
from syntask.concurrency.v1.context import ConcurrencyContext
from syntask.concurrency.v1.sync import concurrency
from syntask.server.schemas.core import ConcurrencyLimit
from syntask.utilities.asyncutils import run_coro_as_sync
from syntask.utilities.timeout import timeout, timeout_async


async def test_concurrency_context_releases_slots_async(
    v1_concurrency_limit: ConcurrencyLimit, syntask_client: SyntaskClient
):
    task_run_id = UUID("00000000-0000-0000-0000-000000000000")

    async def expensive_task():
        async with aconcurrency(v1_concurrency_limit.tag, task_run_id):
            response = await syntask_client.read_concurrency_limit_by_tag(
                v1_concurrency_limit.tag
            )
            assert response.active_slots == [task_run_id]

            # Occupy the slot for longer than the timeout
            await asyncio.sleep(1)

    with pytest.raises(TimeoutError):
        with timeout_async(seconds=0.5):
            with ConcurrencyContext():
                await expensive_task()

    response = await syntask_client.read_concurrency_limit_by_tag(
        v1_concurrency_limit.tag
    )
    assert response.active_slots == []


async def test_concurrency_context_releases_slots_sync(
    v1_concurrency_limit: ConcurrencyLimit, syntask_client: SyntaskClient
):
    task_run_id = UUID("00000000-0000-0000-0000-000000000000")

    def expensive_task():
        with concurrency(v1_concurrency_limit.tag, task_run_id):
            client = get_client()
            response = run_coro_as_sync(
                client.read_concurrency_limit_by_tag(v1_concurrency_limit.tag)
            )
            assert response and response.active_slots == [task_run_id]

            # Occupy the slot for longer than the timeout
            time.sleep(1)

    with pytest.raises(TimeoutError):
        with timeout(seconds=0.5):
            with ConcurrencyContext():
                expensive_task()

    response = await syntask_client.read_concurrency_limit_by_tag(
        v1_concurrency_limit.tag
    )
    assert response.active_slots == []
