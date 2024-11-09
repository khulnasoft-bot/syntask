import platform
import sqlite3
import sys
from unittest.mock import MagicMock, Mock

import pendulum
import pytest

import syntask
from syntask.client.constants import SERVER_API_VERSION
from syntask.settings import SYNTASK_API_URL, SYNTASK_CLOUD_API_URL, temporary_settings
from syntask.testing.cli import invoke_and_assert


def test_version_ephemeral_server_type():
    invoke_and_assert(
        ["version"], expected_output_contains="Server type:         ephemeral"
    )


@pytest.mark.usefixtures("use_hosted_api_server")
def test_version_server_server_type():
    invoke_and_assert(
        ["version"], expected_output_contains="Server type:         server"
    )


def test_version_cloud_server_type():
    with temporary_settings(
        {
            SYNTASK_API_URL: (
                SYNTASK_CLOUD_API_URL.value() + "/accounts/<test>/workspaces/<test>"
            )
        }
    ):
        invoke_and_assert(
            ["version"], expected_output_contains="Server type:         cloud"
        )


def test_version_client_error_server_type(monkeypatch):
    monkeypatch.setattr("syntask.get_client", MagicMock(side_effect=ValueError))
    invoke_and_assert(
        ["version"], expected_output_contains="Server type:         <client error>"
    )


def test_correct_output_ephemeral_sqlite(monkeypatch):
    version_info = syntask.__version_info__
    built = pendulum.parse(syntask.__version_info__["date"])
    profile = syntask.context.get_settings_context().profile

    dialect = Mock()
    dialect().name = "sqlite"
    monkeypatch.setattr("syntask.server.utilities.database.get_dialect", dialect)

    invoke_and_assert(
        ["version"],
        expected_output=f"""Version:             {syntask.__version__}
API version:         {SERVER_API_VERSION}
Python version:      {platform.python_version()}
Git commit:          {version_info['full-revisionid'][:8]}
Built:               {built.to_day_datetime_string()}
OS/Arch:             {sys.platform}/{platform.machine()}
Profile:             {profile.name}
Server type:         ephemeral
Server:
  Database:          sqlite
  SQLite version:    {sqlite3.sqlite_version}
""",
    )


def test_correct_output_ephemeral_postgres(monkeypatch):
    version_info = syntask.__version_info__
    built = pendulum.parse(syntask.__version_info__["date"])
    profile = syntask.context.get_settings_context().profile

    dialect = Mock()
    dialect().name = "postgres"
    monkeypatch.setattr("syntask.server.utilities.database.get_dialect", dialect)

    invoke_and_assert(
        ["version"],
        expected_output=f"""Version:             {syntask.__version__}
API version:         {SERVER_API_VERSION}
Python version:      {platform.python_version()}
Git commit:          {version_info['full-revisionid'][:8]}
Built:               {built.to_day_datetime_string()}
OS/Arch:             {sys.platform}/{platform.machine()}
Profile:             {profile.name}
Server type:         ephemeral
Server:
  Database:          postgres
""",
    )


@pytest.mark.usefixtures("use_hosted_api_server")
def test_correct_output_non_ephemeral_server_type():
    version_info = syntask.__version_info__
    built = pendulum.parse(syntask.__version_info__["date"])
    profile = syntask.context.get_settings_context().profile

    invoke_and_assert(
        ["version"],
        expected_output=f"""Version:             {syntask.__version__}
API version:         {SERVER_API_VERSION}
Python version:      {platform.python_version()}
Git commit:          {version_info['full-revisionid'][:8]}
Built:               {built.to_day_datetime_string()}
OS/Arch:             {sys.platform}/{platform.machine()}
Profile:             {profile.name}
Server type:         server
""",
    )
