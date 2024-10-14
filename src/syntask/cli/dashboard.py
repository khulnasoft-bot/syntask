import webbrowser

from syntask.cli._types import SyntaskTyper
from syntask.cli._utilities import exit_with_success
from syntask.cli.cloud import get_current_workspace
from syntask.cli.root import app
from syntask.client.cloud import CloudUnauthorizedError, get_cloud_client
from syntask.settings import SYNTASK_UI_URL
from syntask.utilities.asyncutils import run_sync_in_worker_thread

dashboard_app = SyntaskTyper(
    name="dashboard",
    help="Commands for interacting with the Syntask UI.",
)
app.add_typer(dashboard_app)


@dashboard_app.command()
async def open():
    """
    Open the Syntask UI in the browser.
    """

    if not (ui_url := SYNTASK_UI_URL.value()):
        raise RuntimeError(
            "`SYNTASK_UI_URL` must be set to the URL of a running Syntask server or Syntask Cloud workspace."
        )

    await run_sync_in_worker_thread(webbrowser.open_new_tab, ui_url)

    async with get_cloud_client() as client:
        try:
            current_workspace = get_current_workspace(await client.read_workspaces())
        except CloudUnauthorizedError:
            current_workspace = None

    destination = (
        f"{current_workspace.account_handle}/{current_workspace.workspace_handle}"
        if current_workspace
        else ui_url
    )

    exit_with_success(f"Opened {destination!r} in browser.")
