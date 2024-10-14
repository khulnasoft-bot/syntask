# Import user-facing API
from syntask.deployments import deploy
from syntask.states import State
from syntask.logging import get_run_logger
from syntask.flows import flow, Flow, serve
from syntask.transactions import Transaction
from syntask.tasks import task, Task
from syntask.context import tags
from syntask.utilities.annotations import unmapped, allow_failure
from syntask.results import BaseResult, ResultRecordMetadata
from syntask.flow_runs import pause_flow_run, resume_flow_run, suspend_flow_run
from syntask.client.orchestration import get_client, SyntaskClient
from syntask.client.cloud import get_cloud_client, CloudClient
import syntask.variables
import syntask.runtime

# Import modules that register types
import syntask.serializers
import syntask.blocks.notifications
import syntask.blocks.system

# Initialize the process-wide profile and registry at import time
import syntask.context

# Perform any forward-ref updates needed for Pydantic models
import syntask.client.schemas

syntask.context.FlowRunContext.model_rebuild(
    _types_namespace={
        "Flow": Flow,
        "BaseResult": BaseResult,
        "ResultRecordMetadata": ResultRecordMetadata,
    }
)
syntask.context.TaskRunContext.model_rebuild(
    _types_namespace={"Task": Task, "BaseResult": BaseResult}
)
syntask.client.schemas.State.model_rebuild(
    _types_namespace={
        "BaseResult": BaseResult,
        "ResultRecordMetadata": ResultRecordMetadata,
    }
)
syntask.client.schemas.StateCreate.model_rebuild(
    _types_namespace={
        "BaseResult": BaseResult,
        "ResultRecordMetadata": ResultRecordMetadata,
    }
)
Transaction.model_rebuild()

# Configure logging
import syntask.logging.configuration

syntask.logging.configuration.setup_logging()
syntask.logging.get_logger("profiles").debug(
    f"Using profile {syntask.context.get_settings_context().profile.name!r}"
)


from syntask._internal.compatibility.deprecated import (
    inject_renamed_module_alias_finder,
)

inject_renamed_module_alias_finder()


# Declare API for type-checkers
__all__ = [
    "allow_failure",
    "flow",
    "Flow",
    "get_client",
    "get_run_logger",
    "State",
    "tags",
    "task",
    "Task",
    "Transaction",
    "unmapped",
    "serve",
    "deploy",
    "pause_flow_run",
    "resume_flow_run",
    "suspend_flow_run",
]
