# isort: skip_file

# Setup version and path constants

from . import _version
import importlib
import pathlib
import warnings
import sys

__version_tuple__ = _version.__version_tuple__
__version__ = _version.__version__

# The absolute path to this module
__module_path__ = pathlib.Path(__file__).parent
# The absolute path to the root of the repository, only valid for use during development
__development_base_path__ = __module_path__.parents[1]

# The absolute path to the built UI within the Python module, used by
# `syntask server start` to serve a dynamic build of the UI
__ui_static_subpath__ = __module_path__ / "server" / "ui_build"

# The absolute path to the built UI within the Python module
__ui_static_path__ = __module_path__ / "server" / "ui"

del _version, pathlib

if sys.version_info < (3, 8):
    warnings.warn(
        (
            "Syntask dropped support for Python 3.7 when it reached end-of-life"
            " . To use new versions of Syntask, you will need"
            " to upgrade to Python 3.8+. See https://devguide.python.org/versions/ for "
            " more details."
        ),
        FutureWarning,
        stacklevel=2,
    )


# Import user-facing API
from syntask.runner import Runner, serve
from syntask.deployments import deploy
from syntask.states import State
from syntask.logging import get_run_logger
from syntask.flows import flow, Flow
from syntask.tasks import task, Task
from syntask.context import tags
from syntask.manifests import Manifest
from syntask.utilities.annotations import unmapped, allow_failure
from syntask.results import BaseResult
from syntask.engine import pause_flow_run, resume_flow_run, suspend_flow_run
from syntask.client.orchestration import get_client, SyntaskClient
from syntask.client.cloud import get_cloud_client, CloudClient
import syntask.variables
import syntask.runtime

# Import modules that register types
import syntask.serializers
import syntask.deprecated.data_documents
import syntask.deprecated.packaging
import syntask.blocks.kubernetes
import syntask.blocks.notifications
import syntask.blocks.system
import syntask.infrastructure.process
import syntask.infrastructure.kubernetes
import syntask.infrastructure.container

# Initialize the process-wide profile and registry at import time
import syntask.context

syntask.context.initialize_object_registry()

# Perform any forward-ref updates needed for Pydantic models
import syntask.client.schemas

syntask.context.FlowRunContext.update_forward_refs(Flow=Flow)
syntask.context.TaskRunContext.update_forward_refs(Task=Task)
syntask.client.schemas.State.update_forward_refs(
    BaseResult=BaseResult, DataDocument=syntask.deprecated.data_documents.DataDocument
)
syntask.client.schemas.StateCreate.update_forward_refs(
    BaseResult=BaseResult, DataDocument=syntask.deprecated.data_documents.DataDocument
)


syntask.plugins.load_extra_entrypoints()

# Configure logging
import syntask.logging.configuration

syntask.logging.configuration.setup_logging()
syntask.logging.get_logger("profiles").debug(
    f"Using profile {syntask.context.get_settings_context().profile.name!r}"
)

# Ensure moved names are accessible at old locations
import syntask.client

syntask.client.get_client = get_client
syntask.client.SyntaskClient = SyntaskClient


from syntask._internal.compatibility.deprecated import (
    inject_renamed_module_alias_finder,
    register_renamed_module,
)

register_renamed_module(
    "syntask.packaging", "syntask.deprecated.packaging", start_date="Mar 2024"
)
inject_renamed_module_alias_finder()


# Attempt to warn users who are importing Syntask 1.x attributes that they may
# have accidentally installed Syntask 2.x

SYNTASK_1_ATTRIBUTES = [
    "syntask.Client",
    "syntask.Parameter",
    "syntask.api",
    "syntask.apply_map",
    "syntask.case",
    "syntask.config",
    "syntask.context",
    "syntask.flatten",
    "syntask.mapped",
    "syntask.models",
    "syntask.resource_manager",
]


class Syntask1ImportInterceptor(importlib.abc.Loader):
    def find_spec(self, fullname, path, target=None):
        if fullname in SYNTASK_1_ATTRIBUTES:
            warnings.warn(
                f"Attempted import of {fullname!r}, which is part of Syntask 1.x, while"
                f" Syntask {__version__} is installed. If you're upgrading you'll need"
                " to update your code, see the Syntask 2.x migration guide:"
                " `https://orion-docs.syntask.io/migration_guide/`. Otherwise ensure"
                " that your code is pinned to the expected version."
            )


if not hasattr(sys, "frozen"):
    sys.meta_path.insert(0, Syntask1ImportInterceptor())


# Declare API for type-checkers
__all__ = [
    "allow_failure",
    "flow",
    "Flow",
    "get_client",
    "get_run_logger",
    "Manifest",
    "State",
    "tags",
    "task",
    "Task",
    "unmapped",
    "Runner",
    "serve",
    "deploy",
    "pause_flow_run",
    "resume_flow_run",
    "suspend_flow_run",
]
