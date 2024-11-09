"""
Command line interface for working with Syntask Server
"""
import json
import os
import platform
import shutil
import subprocess
import sys
import textwrap
import time
from functools import partial
from string import Template
from typing import List

import anyio
import typer

import syntask
from syntask.cli._types import SyntaskTyper, SettingsOption
from syntask.cli._utilities import exit_with_error, exit_with_success
from syntask.cli.agent import start as start_agent
from syntask.cli.root import app
from syntask.settings import (
    SYNTASK_API_URL,
    SYNTASK_CLI_COLORS,
    SYNTASK_CLI_WRAP_LINES,
    SYNTASK_SERVER_API_HOST,
    SYNTASK_SERVER_API_PORT,
)
from syntask.utilities.dockerutils import get_syntask_image_name, python_version_minor
from syntask.utilities.filesystem import tmpchdir
from syntask.utilities.processutils import run_process

DEV_HELP = """
Commands for development.

Note that many of these commands require extra dependencies (such as npm and MkDocs)
to function properly.
"""
dev_app = SyntaskTyper(
    name="dev", short_help="Commands for development.", help=DEV_HELP
)
app.add_typer(dev_app)


def exit_with_error_if_not_editable_install():
    if (
        syntask.__module_path__.parent == "site-packages"
        or not (syntask.__development_base_path__ / "setup.py").exists()
    ):
        exit_with_error(
            "Development commands require an editable Syntask installation. "
            "Development commands require content outside of the 'syntask' module  "
            "which is not available when installed into your site-packages. "
            f"Detected module path: {syntask.__module_path__}."
        )


def agent_process_entrypoint(**kwargs):
    """
    An entrypoint for starting an agent in a subprocess. Adds a Rich console
    to the Typer app, processes Typer default parameters, then starts an agent.
    All kwargs are forwarded to  `syntask.cli.agent.start`.
    """
    import inspect

    import rich

    # import locally so only the `dev` command breaks if Typer internals change
    from typer.models import ParameterInfo

    # Typer does not process default parameters when calling a function
    # directly, so we must set `start_agent`'s default parameters manually.
    # get the signature of the `start_agent` function
    start_agent_signature = inspect.signature(start_agent)

    # for any arguments not present in kwargs, use the default value.
    for name, param in start_agent_signature.parameters.items():
        if name not in kwargs:
            # All `param.default` values for start_agent are Typer params that store the
            # actual default value in their `default` attribute and we must call
            # `param.default.default` to get the actual default value. We should also
            # ensure we extract the right default if non-Typer defaults are added
            # to `start_agent` in the future.
            if isinstance(param.default, ParameterInfo):
                default = param.default.default
            else:
                default = param.default

            # Some defaults are Syntask `SettingsOption.value` methods
            # that must be called to get the actual value.
            kwargs[name] = default() if callable(default) else default

    # add a console, because calling the agent start function directly
    # instead of via CLI call means `app` has no `console` attached.
    app.console = (
        rich.console.Console(
            highlight=False,
            color_system="auto" if SYNTASK_CLI_COLORS else None,
            soft_wrap=not SYNTASK_CLI_WRAP_LINES.value(),
        )
        if not getattr(app, "console", None)
        else app.console
    )

    try:
        start_agent(**kwargs)  # type: ignore
    except KeyboardInterrupt:
        # expected when watchfiles kills the process
        pass


@dev_app.command()
def build_docs(
    schema_path: str = None,
):
    """
    Builds REST API reference documentation for static display.
    """
    exit_with_error_if_not_editable_install()

    from syntask.server.api.server import create_app

    schema = create_app(ephemeral=True).openapi()

    if not schema_path:
        schema_path = (
            syntask.__development_base_path__ / "docs" / "api-ref" / "schema.json"
        ).absolute()
    # overwrite info for display purposes
    schema["info"] = {}
    with open(schema_path, "w") as f:
        json.dump(schema, f)
    app.console.print(f"OpenAPI schema written to {schema_path}")


BUILD_UI_HELP = f"""
Installs dependencies and builds UI locally.

The built UI will be located at {syntask.__development_base_path__ / "ui"}

Requires npm.
"""


@dev_app.command(help=BUILD_UI_HELP)
def build_ui(
    no_install: bool = False,
):
    exit_with_error_if_not_editable_install()
    with tmpchdir(syntask.__development_base_path__ / "ui"):
        if not no_install:
            app.console.print("Installing npm packages...")
            try:
                subprocess.check_output(["npm", "ci"], shell=sys.platform == "win32")
            except Exception:
                app.console.print(
                    "npm call failed - try running `nvm use` first.", style="red"
                )
                raise
            app.console.print("Building for distribution...")
            env = os.environ.copy()
            subprocess.check_output(
                ["npm", "run", "build"], env=env, shell=sys.platform == "win32"
            )

    with tmpchdir(syntask.__development_base_path__):
        if os.path.exists(syntask.__ui_static_path__):
            app.console.print("Removing existing build files...")
            shutil.rmtree(syntask.__ui_static_path__)

        app.console.print("Copying build into src...")
        shutil.copytree("ui/dist", syntask.__ui_static_path__)

    app.console.print("Complete!")


@dev_app.command()
async def ui():
    """
    Starts a hot-reloading development UI.
    """
    exit_with_error_if_not_editable_install()
    with tmpchdir(syntask.__development_base_path__ / "ui"):
        app.console.print("Installing npm packages...")
        await run_process(["npm", "install"], stream_output=True)

        app.console.print("Starting UI development server...")
        await run_process(command=["npm", "run", "serve"], stream_output=True)


@dev_app.command()
async def api(
    host: str = SettingsOption(SYNTASK_SERVER_API_HOST),
    port: int = SettingsOption(SYNTASK_SERVER_API_PORT),
    log_level: str = "DEBUG",
    services: bool = True,
):
    """
    Starts a hot-reloading development API.
    """
    import watchfiles

    server_env = os.environ.copy()
    server_env["SYNTASK_API_SERVICES_RUN_IN_APP"] = str(services)
    server_env["SYNTASK_API_SERVICES_UI"] = "False"
    server_env["SYNTASK_UI_API_URL"] = f"http://{host}:{port}/api"

    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "--factory",
        "syntask.server.api.server:create_app",
        "--host",
        str(host),
        "--port",
        str(port),
        "--log-level",
        log_level.lower(),
    ]

    app.console.print(f"Running: {' '.join(command)}")
    import signal

    stop_event = anyio.Event()
    start_command = partial(
        run_process, command=command, env=server_env, stream_output=True
    )

    async with anyio.create_task_group() as tg:
        try:
            server_pid = await tg.start(start_command)
            async for _ in watchfiles.awatch(
                syntask.__module_path__,
                stop_event=stop_event,  # type: ignore
            ):
                # when any watched files change, restart the server
                app.console.print("Restarting Syntask Server...")
                os.kill(server_pid, signal.SIGTERM)  # type: ignore
                # start a new server
                server_pid = await tg.start(start_command)
        except RuntimeError as err:
            # a bug in watchfiles causes an 'Already borrowed' error from Rust when
            # exiting: https://github.com/samuelcolvin/watchfiles/issues/200
            if str(err).strip() != "Already borrowed":
                raise
        except KeyboardInterrupt:
            # exit cleanly on ctrl-c by killing the server process if it's
            # still running
            try:
                os.kill(server_pid, signal.SIGTERM)  # type: ignore
            except ProcessLookupError:
                # process already exited
                pass

            stop_event.set()


@dev_app.command()
async def agent(
    api_url: str = SettingsOption(SYNTASK_API_URL),
    work_queues: List[str] = typer.Option(
        ["default"],
        "-q",
        "--work-queue",
        help="One or more work queue names for the agent to pull from.",
    ),
):
    """
    Starts a hot-reloading development agent process.
    """
    # Delayed import since this is only a 'dev' dependency
    import watchfiles

    app.console.print("Creating hot-reloading agent process...")

    try:
        await watchfiles.arun_process(
            syntask.__module_path__,
            target=agent_process_entrypoint,
            kwargs=dict(api=api_url, work_queues=work_queues),
        )
    except RuntimeError as err:
        # a bug in watchfiles causes an 'Already borrowed' error from Rust when
        # exiting: https://github.com/samuelcolvin/watchfiles/issues/200
        if str(err).strip() != "Already borrowed":
            raise


@dev_app.command()
async def start(
    exclude_api: bool = typer.Option(False, "--no-api"),
    exclude_ui: bool = typer.Option(False, "--no-ui"),
    exclude_agent: bool = typer.Option(False, "--no-agent"),
    work_queues: List[str] = typer.Option(
        ["default"],
        "-q",
        "--work-queue",
        help="One or more work queue names for the dev agent to pull from.",
    ),
):
    """
    Starts a hot-reloading development server with API, UI, and agent processes.

    Each service has an individual command if you wish to start them separately.
    Each service can be excluded here as well.
    """
    async with anyio.create_task_group() as tg:
        if not exclude_api:
            tg.start_soon(
                partial(
                    api,
                    host=SYNTASK_SERVER_API_HOST.value(),
                    port=SYNTASK_SERVER_API_PORT.value(),
                )
            )
        if not exclude_ui:
            tg.start_soon(ui)
        if not exclude_agent:
            # Hook the agent to the hosted API if running
            if not exclude_api:
                host = f"http://{SYNTASK_SERVER_API_HOST.value()}:{SYNTASK_SERVER_API_PORT.value()}/api"  # noqa
            else:
                host = SYNTASK_API_URL.value()
            tg.start_soon(agent, host, work_queues)


@dev_app.command()
def build_image(
    arch: str = typer.Option(
        None,
        help=(
            "The architecture to build the container for. "
            "Defaults to the architecture of the host Python. "
            f"[default: {platform.machine()}]"
        ),
    ),
    python_version: str = typer.Option(
        None,
        help=(
            "The Python version to build the container for. "
            "Defaults to the version of the host Python. "
            f"[default: {python_version_minor()}]"
        ),
    ),
    flavor: str = typer.Option(
        None,
        help=(
            "An alternative flavor to build, for example 'conda'. "
            "Defaults to the standard Python base image"
        ),
    ),
    dry_run: bool = False,
):
    """
    Build a docker image for development.
    """
    exit_with_error_if_not_editable_install()
    # TODO: Once https://github.com/tiangolo/typer/issues/354 is addressed, the
    #       default can be set in the function signature
    arch = arch or platform.machine()
    python_version = python_version or python_version_minor()

    tag = get_syntask_image_name(python_version=python_version, flavor=flavor)

    # Here we use a subprocess instead of the docker-py client to easily stream output
    # as it comes
    command = [
        "docker",
        "build",
        str(syntask.__development_base_path__),
        "--tag",
        tag,
        "--platform",
        f"linux/{arch}",
        "--build-arg",
        "SYNTASK_EXTRAS=[dev]",
        "--build-arg",
        f"PYTHON_VERSION={python_version}",
    ]

    if flavor:
        command += ["--build-arg", f"BASE_IMAGE=syntask-{flavor}"]

    if dry_run:
        print(" ".join(command))
        return

    try:
        subprocess.check_call(command, shell=sys.platform == "win32")
    except subprocess.CalledProcessError:
        exit_with_error("Failed to build image!")
    else:
        exit_with_success(f"Built image {tag!r} for linux/{arch}")


@dev_app.command()
def container(bg: bool = False, name="syntask-dev", api: bool = True, tag: str = None):
    """
    Run a docker container with local code mounted and installed.
    """
    exit_with_error_if_not_editable_install()
    import docker
    from docker.models.containers import Container

    client = docker.from_env()

    containers = client.containers.list()
    container_names = {container.name for container in containers}
    if name in container_names:
        exit_with_error(
            f"Container {name!r} already exists. Specify a different name or stop "
            "the existing container."
        )

    blocking_cmd = "syntask dev api" if api else "sleep infinity"
    tag = tag or get_syntask_image_name()

    container: Container = client.containers.create(
        image=tag,
        command=[
            "/bin/bash",
            "-c",
            (  # noqa
                "pip install -e /opt/syntask/repo\\[dev\\] && touch /READY &&"
                f" {blocking_cmd}"
            ),
        ],
        name=name,
        auto_remove=True,
        working_dir="/opt/syntask/repo",
        volumes=[f"{syntask.__development_base_path__}:/opt/syntask/repo"],
        shm_size="4G",
    )

    print(f"Starting container for image {tag!r}...")
    container.start()

    print("Waiting for installation to complete", end="", flush=True)
    try:
        ready = False
        while not ready:
            print(".", end="", flush=True)
            result = container.exec_run("test -f /READY")
            ready = result.exit_code == 0
            if not ready:
                time.sleep(3)
    except BaseException:
        print("\nInterrupted. Stopping container...")
        container.stop()
        raise

    print(
        textwrap.dedent(
            f"""
            Container {container.name!r} is ready! To connect to the container, run:

                docker exec -it {container.name} /bin/bash
            """
        )
    )

    if bg:
        print(
            textwrap.dedent(
                f"""
                The container will run forever. Stop the container with:

                    docker stop {container.name}
                """
            )
        )
        # Exit without stopping
        return

    try:
        print("Send a keyboard interrupt to exit...")
        container.wait()
    except KeyboardInterrupt:
        pass  # Avoid showing "Abort"
    finally:
        print("\nStopping container...")
        container.stop()


@dev_app.command()
def kubernetes_manifest():
    """
    Generates a Kubernetes manifest for development.

    Example:
        $ syntask dev kubernetes-manifest | kubectl apply -f -
    """
    exit_with_error_if_not_editable_install()

    template = Template(
        (
            syntask.__module_path__ / "cli" / "templates" / "kubernetes-dev.yaml"
        ).read_text()
    )
    manifest = template.substitute(
        {
            "syntask_root_directory": syntask.__development_base_path__,
            "image_name": get_syntask_image_name(),
        }
    )
    print(manifest)
