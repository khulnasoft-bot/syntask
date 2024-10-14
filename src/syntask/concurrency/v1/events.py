from typing import Dict, List, Literal, Optional, Union
from uuid import UUID

from syntask.client.schemas.responses import MinimalConcurrencyLimitResponse
from syntask.events import Event, RelatedResource, emit_event


def _emit_concurrency_event(
    phase: Union[Literal["acquired"], Literal["released"]],
    primary_limit: MinimalConcurrencyLimitResponse,
    related_limits: List[MinimalConcurrencyLimitResponse],
    task_run_id: UUID,
    follows: Union[Event, None] = None,
) -> Union[Event, None]:
    resource: Dict[str, str] = {
        "syntask.resource.id": f"syntask.concurrency-limit.v1.{primary_limit.id}",
        "syntask.resource.name": primary_limit.name,
        "limit": str(primary_limit.limit),
        "task_run_id": str(task_run_id),
    }

    related = [
        RelatedResource.model_validate(
            {
                "syntask.resource.id": f"syntask.concurrency-limit.v1.{limit.id}",
                "syntask.resource.role": "concurrency-limit",
            }
        )
        for limit in related_limits
        if limit.id != primary_limit.id
    ]

    return emit_event(
        f"syntask.concurrency-limit.v1.{phase}",
        resource=resource,
        related=related,
        follows=follows,
    )


def _emit_concurrency_acquisition_events(
    limits: List[MinimalConcurrencyLimitResponse],
    task_run_id: UUID,
) -> Dict[UUID, Optional[Event]]:
    events = {}
    for limit in limits:
        event = _emit_concurrency_event("acquired", limit, limits, task_run_id)
        events[limit.id] = event

    return events


def _emit_concurrency_release_events(
    limits: List[MinimalConcurrencyLimitResponse],
    events: Dict[UUID, Optional[Event]],
    task_run_id: UUID,
) -> None:
    for limit in limits:
        _emit_concurrency_event(
            "released", limit, limits, task_run_id, events[limit.id]
        )
