import urllib.parse
from typing import Any, Mapping, Optional

from jinja2 import pass_context

from syntask.server.schemas.core import (
    Deployment,
    Flow,
    FlowRun,
    TaskRun,
    WorkPool,
    WorkQueue,
)
from syntask.server.schemas.responses import WorkQueueWithStatus
from syntask.server.utilities.schemas import ORMBaseModel
from syntask.settings import SYNTASK_UI_URL
from syntask.utilities.urls import url_for

model_to_kind = {
    Deployment: "syntask.deployment",
    Flow: "syntask.flow",
    FlowRun: "syntask.flow-run",
    TaskRun: "syntask.task-run",
    WorkQueue: "syntask.work-queue",
    WorkQueueWithStatus: "syntask.work-queue",
    WorkPool: "syntask.work-pool",
}


@pass_context
def ui_url(ctx: Mapping[str, Any], obj: Any) -> Optional[str]:
    """Return the UI URL for the given object."""
    return url_for(obj, url_type="ui")


@pass_context
def ui_resource_events_url(ctx: Mapping[str, Any], obj: Any) -> Optional[str]:
    """Given a Resource or Model, return a UI link to the events page
    filtered for that resource. If an unsupported object is provided,
    return `None`.

    Currently supports Automation, Resource, Deployment, Flow, FlowRun, TaskRun, and
    WorkQueue objects. Within a Resource, deployment, flow, flow-run, task-run,
    and work-queue are supported."""
    from syntask.server.events.schemas.automations import Automation
    from syntask.server.events.schemas.events import Resource

    url = None
    url_format = "events?resource={resource_id}"

    if isinstance(obj, Automation):
        url = url_format.format(resource_id=f"syntask.automation.{obj.id}")
    elif isinstance(obj, Resource):
        kind, _, id = obj.id.rpartition(".")
        url = url_format.format(resource_id=f"{kind}.{id}")
    elif isinstance(obj, ORMBaseModel):
        kind = model_to_kind.get(type(obj))  # type: ignore

        if kind:
            url = url_format.format(resource_id=f"{kind}.{obj.id}")
    if url:
        return urllib.parse.urljoin(SYNTASK_UI_URL.value(), url)
    else:
        return None


all_filters = {"ui_url": ui_url, "ui_resource_events_url": ui_resource_events_url}
