"""
This module provides a function to handle imports for moved or removed objects in Syntask 3.0 upgrade.

The `getattr_migration` function is used to handle imports for moved or removed objects in Syntask 3.0 upgrade.
It is used in the `__getattr__` attribute of modules that have moved or removed objects.

Usage:

Moved objects:
1. Add the old and new path to the `MOVED_IN_V3` dictionary, e.g. `MOVED_IN_V3 = {"old_path": "new_path"}`
2. In the module where the object was moved from, add the following lines:
    ```python
    # at top
    from syntask._internal.compatibility.migration import getattr_migration

    # at bottom
    __getattr__ = getattr_migration(__name__)
    ```

    Example at src/syntask/engine.py

Removed objects:
1. Add the old path and error message to the `REMOVED_IN_V3` dictionary, e.g. `REMOVED_IN_V3 = {"old_path": "error_message"}`
2. In the module where the object was removed, add the following lines:
    ```python
    # at top
    from syntask._internal.compatibility.migration import getattr_migration

    # at bottom
    __getattr__ = getattr_migration(__name__)

    ```
    If the entire old module was removed, add a stub for the module with the following lines:
    ```python
    # at top
    from syntask._internal.compatibility.migration import getattr_migration

    # at bottom
    __getattr__ = getattr_migration(__name__)
    ```

    Example at src/syntask/infrastructure/base.py
"""

import sys
from typing import Any, Callable, Dict

from pydantic_core import PydanticCustomError

from syntask.exceptions import SyntaskImportError

MOVED_IN_V3 = {
    "syntask.deployments.deployments:load_flow_from_flow_run": "syntask.flows:load_flow_from_flow_run",
    "syntask.deployments:load_flow_from_flow_run": "syntask.flows:load_flow_from_flow_run",
    "syntask.variables:get": "syntask.variables:Variable.get",
    "syntask.engine:pause_flow_run": "syntask.flow_runs:pause_flow_run",
    "syntask.engine:resume_flow_run": "syntask.flow_runs:resume_flow_run",
    "syntask.engine:suspend_flow_run": "syntask.flow_runs:suspend_flow_run",
    "syntask.engine:_in_process_pause": "syntask.flow_runs:_in_process_pause",
    "syntask.client:get_client": "syntask.client.orchestration:get_client",
}

upgrade_guide_msg = "Refer to the upgrade guide for more information: https://docs.syntask.khulnasoft.com/latest/resources/upgrade-agents-to-workers."

REMOVED_IN_V3 = {
    "syntask.client.schemas.objects:MinimalDeploymentSchedule": "Use `syntask.client.schemas.actions.DeploymentScheduleCreate` instead.",
    "syntask.context:SyntaskObjectRegistry": upgrade_guide_msg,
    "syntask.deployments.deployments:Deployment": "Use `flow.serve()`, `flow.deploy()`, or `syntask deploy` instead.",
    "syntask.deployments:Deployment": "Use `flow.serve()`, `flow.deploy()`, or `syntask deploy` instead.",
    "syntask.filesystems:GCS": "Use `syntask_gcp.GcsBucket` instead.",
    "syntask.filesystems:Azure": "Use `syntask_azure.AzureBlobStorageContainer` instead.",
    "syntask.filesystems:S3": "Use `prefect_aws.S3Bucket` instead.",
    "syntask.filesystems:GitHub": "Use `syntask_github.GitHubRepository` instead.",
    "syntask.engine:_out_of_process_pause": "Use `syntask.flow_runs.pause_flow_run` instead.",
    "syntask.agent:SyntaskAgent": "Use workers instead. " + upgrade_guide_msg,
    "syntask.infrastructure:KubernetesJob": "Use workers instead. " + upgrade_guide_msg,
    "syntask.infrastructure.base:Infrastructure": "Use the `BaseWorker` class to create custom infrastructure integrations instead. "
    + upgrade_guide_msg,
    "syntask.workers.block:BlockWorkerJobConfiguration": upgrade_guide_msg,
    "syntask.workers.cloud:BlockWorker": upgrade_guide_msg,
}

# IMPORTANT FOR USAGE: When adding new modules to MOVED_IN_V3 or REMOVED_IN_V3, include the following lines at the bottom of that module:
# from syntask._internal.compatibility.migration import getattr_migration
# __getattr__ = getattr_migration(__name__)
# See src/syntask/filesystems.py for an example


def import_string_class_method(new_location: str) -> Callable:
    """
    Handle moved class methods.

    `import_string` does not account for moved class methods. This function handles cases where a method has been
    moved to a class. For example, if `new_location` is 'syntask.variables:Variable.get', `import_string(new_location)`
    will raise an error because it does not handle class methods. This function will import the class and get the
    method from the class.

    Args:
        new_location (str): The new location of the method.

    Returns:
        method: The resolved method from the class.

    Raises:
        SyntaskImportError: If the method is not found in the class.
    """
    from pydantic._internal._validators import import_string

    class_name, method_name = new_location.rsplit(".", 1)

    cls = import_string(class_name)
    method = getattr(cls, method_name, None)

    if method is not None and callable(method):
        return method

    raise SyntaskImportError(f"Unable to import {new_location!r}")


def getattr_migration(module_name: str) -> Callable[[str], Any]:
    """
    Handle imports for moved or removed objects in Syntask 3.0 upgrade

    Args:
        module_name (str): The name of the module to handle imports for.
    """

    def wrapper(name: str) -> object:
        """
        Raise a SyntaskImportError if the object is not found, moved, or removed.
        """

        if name == "__path__":
            raise AttributeError(f"{module_name!r} object has no attribute {name!r}")
        import warnings

        from pydantic._internal._validators import import_string

        import_path = f"{module_name}:{name}"

        # Check if the attribute name corresponds to a moved or removed class or module
        if import_path in MOVED_IN_V3.keys():
            new_location = MOVED_IN_V3[import_path]
            warnings.warn(
                f"{import_path!r} has been moved to {new_location!r}. Importing from {new_location!r} instead. This warning will raise an error in a future release.",
                DeprecationWarning,
                stacklevel=2,
            )
            try:
                return import_string(new_location)
            except PydanticCustomError:
                return import_string_class_method(new_location)

        if import_path in REMOVED_IN_V3.keys():
            error_message = REMOVED_IN_V3[import_path]
            raise SyntaskImportError(
                f"`{import_path}` has been removed. {error_message}"
            )

        globals: Dict[str, Any] = sys.modules[module_name].__dict__
        if name in globals:
            return globals[name]

        raise AttributeError(f"module {module_name!r} has no attribute {name!r}")

    return wrapper
