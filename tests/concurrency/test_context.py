import asyncio
import time

import pytest

from syntask.client.orchestration import SyntaskClient, get_client
from syntask.concurrency.asyncio import concurrency as aconcurrency
from syntask.concurrency.context import ConcurrencyContext
from syntask.concurrency.sync import concurrency
from syntask.server.schemas.core import ConcurrencyLimitV2
from syntask.utilities.asyncutils import run_coro_as_sync
from syntask.utilities.timeout import timeout, timeout_async


async def test_concurrency_context_releases_slots_async(
    concurrency_limit: ConcurrencyLimitV2, syntask_client: SyntaskClient
):
    async def expensive_task():
        async with aconcurrency(concurrency_limit.name):
            response = await syntask_client.read_global_concurrency_limit_by_name(
                concurrency_limit.name
            )
            assert response.active_slots == 1

            # Occupy the slot for longer than the timeout
            await asyncio.sleep(1)

    with pytest.raises(TimeoutError):
        with timeout_async(seconds=0.5):
            with ConcurrencyContext():
                await expensive_task()

    response = await syntask_client.read_global_concurrency_limit_by_name(
        concurrency_limit.name
    )
    assert response.active_slots == 0


async def test_concurrency_context_releases_slots_sync(
    concurrency_limit: ConcurrencyLimitV2, syntask_client: SyntaskClient
):
    def expensive_task():
        with concurrency(concurrency_limit.name):
            client = get_client()
            response = run_coro_as_sync(
                client.read_global_concurrency_limit_by_name(concurrency_limit.name)
            )
            assert response and response.active_slots == 1

            # Occupy the slot for longer than the timeout
            time.sleep(1)

    with pytest.raises(TimeoutError):
        with timeout(seconds=0.5):
            with ConcurrencyContext():
                expensive_task()

    response = await syntask_client.read_global_concurrency_limit_by_name(
        concurrency_limit.name
    )
    assert response.active_slots == 0
