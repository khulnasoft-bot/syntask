"""
Base `syntask` command-line application
"""

import asyncio
import platform
import sys
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as import_version
from typing import Any, Dict

import pendulum
import typer

import syntask
import syntask.context
import syntask.settings
from syntask.cli._types import SettingsOption, SyntaskTyper
from syntask.cli._utilities import with_cli_exception_handling
from syntask.client.base import determine_server_type
from syntask.client.constants import SERVER_API_VERSION
from syntask.client.orchestration import ServerType
from syntask.logging.configuration import setup_logging
from syntask.settings import (
    SYNTASK_CLI_WRAP_LINES,
    SYNTASK_TEST_MODE,
)

app = SyntaskTyper(add_completion=True, no_args_is_help=True)


def version_callback(value: bool):
    if value:
        print(syntask.__version__)
        raise typer.Exit()


def is_interactive():
    return app.console.is_interactive


@app.callback()
@with_cli_exception_handling
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        # A callback is necessary for Typer to call this without looking for additional
        # commands and erroring when excluded
        callback=version_callback,
        help="Display the current version.",
        is_eager=True,
    ),
    profile: str = typer.Option(
        None,
        "--profile",
        "-p",
        help="Select a profile for this CLI run.",
        is_eager=True,
    ),
    prompt: bool = SettingsOption(
        syntask.settings.SYNTASK_CLI_PROMPT,
        help="Force toggle prompts for this CLI run.",
    ),
):
    if profile and not syntask.context.get_settings_context().profile.name == profile:
        # Generally, the profile should entered by `enter_root_settings_context`.
        # In the cases where it is not (i.e. CLI testing), we will enter it here.
        settings_ctx = syntask.context.use_profile(
            profile, override_environment_variables=True
        )
        try:
            ctx.with_resource(settings_ctx)
        except KeyError:
            print(f"Unknown profile {profile!r}.")
            exit(1)

    # Configure the output console after loading the profile
    app.setup_console(soft_wrap=SYNTASK_CLI_WRAP_LINES.value(), prompt=prompt)

    if not SYNTASK_TEST_MODE:
        # When testing, this entrypoint can be called multiple times per process which
        # can cause logging configuration conflicts. Logging is set up in conftest
        # during tests.
        setup_logging()

    # When running on Windows we need to ensure that the correct event loop policy is
    # in place or we will not be able to spawn subprocesses. Sometimes this policy is
    # changed by other libraries, but here in our CLI we should have ownership of the
    # process and be able to safely force it to be the correct policy.
    # https://github.com/synopkg/syntask/issues/8206
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


@app.command()
async def version(
    omit_integrations: bool = typer.Option(
        False, "--omit-integrations", help="Omit integration information"
    ),
):
    """Get the current Syntask version and integration information."""
    import sqlite3

    from syntask.server.utilities.database import get_dialect
    from syntask.settings import SYNTASK_API_DATABASE_CONNECTION_URL

    version_info = {
        "Version": syntask.__version__,
        "API version": SERVER_API_VERSION,
        "Python version": platform.python_version(),
        "Git commit": syntask.__version_info__["full-revisionid"][:8],
        "Built": pendulum.parse(
            syntask.__version_info__["date"]
        ).to_day_datetime_string(),
        "OS/Arch": f"{sys.platform}/{platform.machine()}",
        "Profile": syntask.context.get_settings_context().profile.name,
    }
    server_type = determine_server_type()

    version_info["Server type"] = server_type.lower()

    try:
        pydantic_version = import_version("pydantic")
    except PackageNotFoundError:
        pydantic_version = "Not installed"

    version_info["Pydantic version"] = pydantic_version

    if server_type == ServerType.EPHEMERAL.value:
        database = get_dialect(SYNTASK_API_DATABASE_CONNECTION_URL.value()).name
        version_info["Server"] = {"Database": database}
        if database == "sqlite":
            version_info["Server"]["SQLite version"] = sqlite3.sqlite_version

    if not omit_integrations:
        integrations = get_syntask_integrations()
        if integrations:
            version_info["Integrations"] = integrations

    display(version_info)


def get_syntask_integrations() -> Dict[str, str]:
    """Get information about installed Syntask integrations."""
    from importlib.metadata import distributions

    integrations = {}
    for dist in distributions():
        if dist.metadata["Name"].startswith("syntask-"):
            author_email = dist.metadata.get("Author-email", "").strip()
            if author_email.endswith("@khulnasoft.com>"):
                integrations[dist.metadata["Name"]] = dist.version

    return integrations


def display(object: Dict[str, Any], nesting: int = 0):
    """Recursive display of a dictionary with nesting."""
    for key, value in object.items():
        key += ":"
        if isinstance(value, dict):
            app.console.print(" " * nesting + key)
            display(value, nesting + 2)
        else:
            prefix = " " * nesting
            app.console.print(f"{prefix}{key.ljust(20 - len(prefix))} {value}")
