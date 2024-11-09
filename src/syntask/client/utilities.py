"""
Utilities for working with clients.
"""

# This module must not import from `syntask.client` when it is imported to avoid
# circular imports for decorators such as `inject_client` which are widely used.

from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Optional, Tuple, cast

from typing_extensions import ParamSpec

if TYPE_CHECKING:
    from syntask.client.orchestration import SyntaskClient

P = ParamSpec("P")


def get_or_create_client(
    client: Optional["SyntaskClient"] = None,
) -> Tuple["SyntaskClient", bool]:
    """
    Returns provided client, infers a client from context if available, or creates a new client.

    Args:
        - client (SyntaskClient, optional): an optional client to use

    Returns:
        - tuple: a tuple of the client and a boolean indicating if the client was inferred from context
    """
    if client is not None:
        return client, True
    from syntask._internal.concurrency.event_loop import get_running_loop
    from syntask.context import FlowRunContext, TaskRunContext

    flow_run_context = FlowRunContext.get()
    task_run_context = TaskRunContext.get()

    if (
        flow_run_context
        and getattr(flow_run_context.client, "_loop") == get_running_loop()
    ):
        return flow_run_context.client, True
    elif (
        task_run_context
        and getattr(task_run_context.client, "_loop") == get_running_loop()
    ):
        return task_run_context.client, True
    else:
        from syntask.client.orchestration import get_client as get_httpx_client

        return get_httpx_client(), False


def inject_client(
    fn: Callable[P, Coroutine[Any, Any, Any]],
) -> Callable[P, Coroutine[Any, Any, Any]]:
    """
    Simple helper to provide a context managed client to a asynchronous function.

    The decorated function _must_ take a `client` kwarg and if a client is passed when
    called it will be used instead of creating a new one, but it will not be context
    managed as it is assumed that the caller is managing the context.
    """

    @wraps(fn)
    async def with_injected_client(*args: P.args, **kwargs: P.kwargs) -> Any:
        client = cast(Optional["SyntaskClient"], kwargs.pop("client", None))
        client, inferred = get_or_create_client(client)
        if not inferred:
            context = client
        else:
            from syntask.utilities.asyncutils import asyncnullcontext

            context = asyncnullcontext()
        async with context as new_client:
            kwargs.setdefault("client", new_client or client)
            return await fn(*args, **kwargs)

    return with_injected_client
