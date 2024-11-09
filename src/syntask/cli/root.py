"""
Base `syntask` command-line application
"""

import asyncio
import platform
import sys

import rich.console
import typer
from rich.theme import Theme

import syntask
import syntask.context
import syntask.settings
from syntask.cli._types import SyntaskTyper, SettingsOption
from syntask.cli._utilities import with_cli_exception_handling
from syntask.client.constants import SERVER_API_VERSION
from syntask.client.orchestration import ServerType
from syntask.logging.configuration import setup_logging
from syntask.settings import (
    SYNTASK_CLI_COLORS,
    SYNTASK_CLI_WRAP_LINES,
    SYNTASK_TEST_MODE,
)

app = SyntaskTyper(add_completion=False, no_args_is_help=True)


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

    app.console = rich.console.Console(
        highlight=False,
        color_system="auto" if SYNTASK_CLI_COLORS else None,
        theme=Theme({"prompt.choices": "bold blue"}),
        # `soft_wrap` disables wrapping when `True`
        soft_wrap=not SYNTASK_CLI_WRAP_LINES.value(),
        force_interactive=prompt,
    )

    if not SYNTASK_TEST_MODE:
        # When testing, this entrypoint can be called multiple times per process which
        # can cause logging configuration conflicts. Logging is set up in conftest
        # during tests.
        setup_logging()

    # When running on Windows we need to ensure that the correct event loop policy is
    # in place or we will not be able to spawn subprocesses. Sometimes this policy is
    # changed by other libraries, but here in our CLI we should have ownership of the
    # process and be able to safely force it to be the correct policy.
    # https://github.com/Synopkg/syntask/issues/8206
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


@app.command()
async def version():
    """Get the current Syntask version."""
    import sqlite3

    from syntask.server.utilities.database import get_dialect
    from syntask.settings import SYNTASK_API_DATABASE_CONNECTION_URL

    version_info = {
        "Version": syntask.__version__,
        "API version": SERVER_API_VERSION,
        "Python version": platform.python_version(),
        "Git commit": syntask.__version_tuple__[-1][:8],
        "OS/Arch": f"{sys.platform}/{platform.machine()}",
        "Profile": syntask.context.get_settings_context().profile.name,
    }

    server_type: str

    try:
        # We do not context manage the client because when using an ephemeral app we do not
        # want to create the database or run migrations
        client = syntask.get_client()
        server_type = client.server_type.value
    except Exception:
        server_type = "<client error>"

    version_info["Server type"] = server_type.lower()

    # TODO: Consider adding an API route to retrieve this information?
    if server_type == ServerType.EPHEMERAL.value:
        database = get_dialect(SYNTASK_API_DATABASE_CONNECTION_URL.value()).name
        version_info["Server"] = {"Database": database}
        if database == "sqlite":
            version_info["Server"]["SQLite version"] = sqlite3.sqlite_version

    def display(object: dict, nesting: int = 0):
        # Recursive display of a dictionary with nesting
        for key, value in object.items():
            key += ":"
            if isinstance(value, dict):
                app.console.print(key)
                return display(value, nesting + 2)
            prefix = " " * nesting
            app.console.print(f"{prefix}{key.ljust(20 - len(prefix))} {value}")

    display(version_info)
