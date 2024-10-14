import shutil
from uuid import uuid4

import pytest
import respx
from httpx import Response

from syntask.cli.profile import show_profile_changes
from syntask.context import use_profile
from syntask.settings import (
    DEFAULT_PROFILES_PATH,
    SYNTASK_API_KEY,
    SYNTASK_API_URL,
    SYNTASK_DEBUG_MODE,
    SYNTASK_PROFILES_PATH,
    Profile,
    ProfilesCollection,
    _read_profiles_from,
    load_profiles,
    save_profiles,
    temporary_settings,
)
from syntask.testing.cli import invoke_and_assert


@pytest.fixture(autouse=True)
def temporary_profiles_path(tmp_path):
    path = tmp_path / "profiles.toml"
    with temporary_settings({SYNTASK_PROFILES_PATH: path}):
        yield path


def test_use_profile_unknown_key():
    invoke_and_assert(
        ["profile", "use", "foo"],
        expected_code=1,
        expected_output="Profile 'foo' not found.",
    )


class TestChangingProfileAndCheckingServerConnection:
    @pytest.fixture
    def profiles(self):
        syntask_cloud_api_url = "https://mock-cloud.syntask.khulnasoft.com/api"
        syntask_cloud_server_api_url = (
            f"{syntask_cloud_api_url}/accounts/{uuid4()}/workspaces/{uuid4()}"
        )
        hosted_server_api_url = "https://hosted-server.syntask.khulnasoft.com/api"

        return ProfilesCollection(
            profiles=[
                Profile(
                    name="syntask-cloud",
                    settings={
                        "SYNTASK_API_URL": syntask_cloud_server_api_url,
                        "SYNTASK_API_KEY": "a working cloud api key",
                    },
                ),
                Profile(
                    name="syntask-cloud-with-invalid-key",
                    settings={
                        "SYNTASK_API_URL": syntask_cloud_server_api_url,
                        "SYNTASK_API_KEY": "a broken cloud api key",
                    },
                ),
                Profile(
                    name="hosted-server",
                    settings={
                        "SYNTASK_API_URL": hosted_server_api_url,
                    },
                ),
                Profile(
                    name="ephemeral",
                    settings={"SYNTASK_SERVER_ALLOW_EPHEMERAL_MODE": True},
                ),
            ],
            active=None,
        )

    @pytest.fixture
    def authorized_cloud(self):
        # attempts to reach the Cloud 2 workspaces endpoint implies a good connection
        # to Syntask Cloud as opposed to a hosted Syntask server instance
        with respx.mock:
            authorized = respx.get(
                "https://mock-cloud.syntask.khulnasoft.com/api/me/workspaces",
            ).mock(return_value=Response(200, json=[]))

            yield authorized

    @pytest.fixture
    def unauthorized_cloud(self):
        # requests to cloud with an invalid key will result in a 401 response
        with respx.mock:
            unauthorized = respx.get(
                "https://mock-cloud.syntask.khulnasoft.com/api/me/workspaces",
            ).mock(return_value=Response(401, json={}))

            yield unauthorized

    @pytest.fixture
    def unhealthy_cloud(self):
        # Cloud may respond with a 500 error when having connection issues
        with respx.mock:
            unhealthy_cloud = respx.get(
                "https://mock-cloud.syntask.khulnasoft.com/api/me/workspaces",
            ).mock(return_value=Response(500, json={}))

            yield unhealthy_cloud

    @pytest.fixture
    def hosted_server_has_no_cloud_api(self):
        # if the API URL points to a hosted Syntask server instance, no Cloud API will be found
        with respx.mock:
            hosted = respx.get(
                "https://hosted-server.syntask.khulnasoft.com/api/me/workspaces",
            ).mock(return_value=Response(404, json={}))

            yield hosted

    @pytest.fixture
    def healthy_hosted_server(self):
        with respx.mock:
            hosted = respx.get(
                "https://hosted-server.syntask.khulnasoft.com/api/health",
            ).mock(return_value=Response(200, json={}))

            yield hosted

    def connection_error(self, *args):
        raise Exception

    @pytest.fixture
    def unhealthy_hosted_server(self):
        with respx.mock:
            badly_hosted = respx.get(
                "https://hosted-server.syntask.khulnasoft.com/api/health",
            ).mock(side_effect=self.connection_error)

            yield badly_hosted

    def test_authorized_cloud_connection(self, authorized_cloud, profiles):
        save_profiles(profiles)
        invoke_and_assert(
            ["profile", "use", "syntask-cloud"],
            expected_output_contains=(
                "Connected to Syntask Cloud using profile 'syntask-cloud'"
            ),
            expected_code=0,
        )

        profiles = load_profiles()
        assert profiles.active_name == "syntask-cloud"

    def test_unauthorized_cloud_connection(self, unauthorized_cloud, profiles):
        save_profiles(profiles)
        invoke_and_assert(
            ["profile", "use", "syntask-cloud-with-invalid-key"],
            expected_output_contains=(
                "Error authenticating with Syntask Cloud using profile"
                " 'syntask-cloud-with-invalid-key'"
            ),
            expected_code=1,
        )

        profiles = load_profiles()
        assert profiles.active_name == "syntask-cloud-with-invalid-key"

    def test_unhealthy_cloud_connection(self, unhealthy_cloud, profiles):
        save_profiles(profiles)
        invoke_and_assert(
            ["profile", "use", "syntask-cloud"],
            expected_output_contains="Error connecting to Syntask Cloud",
            expected_code=1,
        )

        profiles = load_profiles()
        assert profiles.active_name == "syntask-cloud"

    def test_using_hosted_server(
        self, hosted_server_has_no_cloud_api, healthy_hosted_server, profiles
    ):
        save_profiles(profiles)
        invoke_and_assert(
            ["profile", "use", "hosted-server"],
            expected_output_contains=(
                "Connected to Syntask server using profile 'hosted-server'"
            ),
            expected_code=0,
        )

        profiles = load_profiles()
        assert profiles.active_name == "hosted-server"

    def test_unhealthy_hosted_server(
        self, hosted_server_has_no_cloud_api, unhealthy_hosted_server, profiles
    ):
        save_profiles(profiles)
        invoke_and_assert(
            ["profile", "use", "hosted-server"],
            expected_output_contains="Error connecting to Syntask server",
            expected_code=1,
        )

        profiles = load_profiles()
        assert profiles.active_name == "hosted-server"

    def test_using_ephemeral_server(self, profiles):
        save_profiles(profiles)
        invoke_and_assert(
            ["profile", "use", "ephemeral"],
            expected_output_contains=(
                "No Syntask server specified using profile 'ephemeral'"
            ),
            expected_code=0,
        )

        profiles = load_profiles()
        assert profiles.active_name == "ephemeral"


def test_ls_additional_profiles():
    # 'ephemeral' is not the current profile because we have a temporary profile in-use
    # during tests

    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="foo", settings={}),
                Profile(name="bar", settings={}),
            ],
            active=None,
        )
    )

    invoke_and_assert(
        ["profile", "ls"],
        expected_output_contains=(
            "foo",
            "bar",
        ),
    )


def test_ls_respects_current_from_profile_flag():
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="foo", settings={}),
            ],
            active=None,
        )
    )

    invoke_and_assert(
        ["--profile", "foo", "profile", "ls"],
        expected_output_contains=("* foo",),
    )


def test_ls_respects_current_from_context():
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="foo", settings={}),
                Profile(name="bar", settings={}),
            ],
            active=None,
        )
    )

    with use_profile("bar"):
        invoke_and_assert(
            ["profile", "ls"],
            expected_output_contains=(
                "foo",
                "* bar",
            ),
        )


def test_create_profile():
    invoke_and_assert(
        ["profile", "create", "foo"],
        expected_output="""
            Created profile with properties:
                name - 'foo'
                from name - None

            Use created profile for future, subsequent commands:
                syntask profile use 'foo'

            Use created profile temporarily for a single command:
                syntask -p 'foo' config view
            """,
    )

    profiles = load_profiles()
    assert profiles["foo"] == Profile(
        name="foo", settings={}, source=SYNTASK_PROFILES_PATH.value()
    )


def test_create_profile_from_existing():
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="foo", settings={SYNTASK_API_KEY: "foo"}),
            ],
            active=None,
        )
    )

    invoke_and_assert(
        ["profile", "create", "bar", "--from", "foo"],
        expected_output="""
            Created profile with properties:
                name - 'bar'
                from name - foo

            Use created profile for future, subsequent commands:
                syntask profile use 'bar'

            Use created profile temporarily for a single command:
                syntask -p 'bar' config view
            """,
    )

    profiles = load_profiles()
    assert profiles["foo"].settings == {SYNTASK_API_KEY: "foo"}, "Foo is unchanged"
    assert profiles["bar"] == Profile(
        name="bar",
        settings={SYNTASK_API_KEY: "foo"},
        source=SYNTASK_PROFILES_PATH.value(),
    )


def test_create_profile_from_unknown_profile():
    invoke_and_assert(
        ["profile", "create", "bar", "--from", "foo"],
        expected_output="Profile 'foo' not found.",
        expected_code=1,
    )


def test_create_profile_with_existing_profile():
    invoke_and_assert(
        ["profile", "create", "ephemeral"],
        expected_output="""
            Profile 'ephemeral' already exists.
            To create a new profile, remove the existing profile first:

                syntask profile delete 'ephemeral'
            """,
        expected_code=1,
    )


def test_delete_profile():
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="foo", settings={SYNTASK_API_KEY: "foo"}),
                Profile(name="bar", settings={SYNTASK_API_KEY: "bar"}),
            ],
            active=None,
        )
    )

    invoke_and_assert(
        ["profile", "delete", "bar"],
        user_input="y",
        expected_output_contains="Removed profile 'bar'.",
    )

    profiles = load_profiles()
    assert "foo" in profiles
    assert "bar" not in profiles


def test_delete_profile_unknown_name():
    invoke_and_assert(
        ["profile", "delete", "foo"],
        expected_output="Profile 'foo' not found.",
        expected_code=1,
    )


def test_delete_profile_cannot_target_active_profile():
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="foo", settings={SYNTASK_API_KEY: "foo"}),
            ],
            active=None,
        )
    )

    with use_profile("foo"):
        invoke_and_assert(
            ["profile", "delete", "foo"],
            expected_output=(
                "Profile 'foo' is the active profile. You must switch profiles before"
                " it can be deleted."
            ),
            expected_code=1,
        )


def test_rename_profile_name_exists():
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="foo", settings={}),
                Profile(name="bar", settings={}),
            ],
            active=None,
        )
    )

    invoke_and_assert(
        ["profile", "rename", "foo", "bar"],
        expected_output="Profile 'bar' already exists.",
        expected_code=1,
    )


def test_rename_profile_unknown_name():
    invoke_and_assert(
        ["profile", "rename", "foo", "bar"],
        expected_output="Profile 'foo' not found.",
        expected_code=1,
    )


def test_rename_profile_renames_profile():
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="foo", settings={SYNTASK_API_KEY: "foo"}),
            ],
            active=None,
        )
    )

    invoke_and_assert(
        ["profile", "rename", "foo", "bar"],
        expected_output="Renamed profile 'foo' to 'bar'.",
        expected_code=0,
    )

    profiles = load_profiles()
    assert "foo" not in profiles, "The original profile should not exist anymore"
    assert profiles["bar"].settings == {
        SYNTASK_API_KEY: "foo"
    }, "Settings should be retained"
    assert profiles.active_name != "bar", "The active profile should not be changed"


def test_rename_profile_changes_active_profile():
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="foo", settings={SYNTASK_API_KEY: "foo"}),
            ],
            active="foo",
        )
    )

    invoke_and_assert(
        ["profile", "rename", "foo", "bar"],
        expected_output="Renamed profile 'foo' to 'bar'.",
        expected_code=0,
    )

    profiles = load_profiles()
    assert profiles.active_name == "bar"


def test_rename_profile_warns_on_environment_variable_active_profile(monkeypatch):
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="foo", settings={SYNTASK_API_KEY: "foo"}),
            ],
            active=None,
        )
    )

    monkeypatch.setenv("SYNTASK_PROFILE", "foo")

    invoke_and_assert(
        ["profile", "rename", "foo", "bar"],
        expected_output_contains=(
            "You have set your current profile to 'foo' with the SYNTASK_PROFILE "
            "environment variable. You must update this variable to 'bar' "
            "to continue using the profile."
        ),
        expected_code=0,
    )

    profiles = load_profiles()
    assert (
        profiles.active_name != "foo"
    ), "The active profile should not be updated in the file"


def test_inspect_profile_unknown_name():
    invoke_and_assert(
        ["profile", "inspect", "foo"],
        expected_output="Profile 'foo' not found.",
        expected_code=1,
    )


def test_inspect_profile():
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(
                    name="foo",
                    settings={SYNTASK_API_KEY: "foo", SYNTASK_DEBUG_MODE: True},
                ),
            ],
            active=None,
        )
    )

    invoke_and_assert(
        ["profile", "inspect", "foo"],
        expected_output="""
            SYNTASK_API_KEY='foo'
            SYNTASK_DEBUG_MODE='True'
            """,
    )


def test_inspect_profile_without_settings():
    save_profiles(
        ProfilesCollection(
            profiles=[Profile(name="foo", settings={})],
            active=None,
        )
    )

    invoke_and_assert(
        ["profile", "inspect", "foo"],
        expected_output="""
            Profile 'foo' is empty.
            """,
    )


class TestProfilesPopulateDefaults:
    def test_populate_defaults(self, temporary_profiles_path):
        default_profiles = _read_profiles_from(DEFAULT_PROFILES_PATH)

        assert not temporary_profiles_path.exists()

        invoke_and_assert(
            ["profile", "populate-defaults"],
            user_input="y",
            expected_output_contains=[
                "Proposed Changes:",
                "Add 'ephemeral'",
                "Add 'local'",
                "Add 'cloud'",
                "Add 'test'",
                f"Profiles updated in {temporary_profiles_path}",
                "Use with syntask profile use [PROFILE-NAME]",
            ],
        )

        assert temporary_profiles_path.exists()

        populated_profiles = load_profiles()

        assert populated_profiles.names == default_profiles.names
        assert populated_profiles.active_name == default_profiles.active_name

        assert {"local", "ephemeral", "cloud", "test"} == set(populated_profiles.names)

        for name in default_profiles.names:
            assert populated_profiles[name].settings == default_profiles[name].settings

    def test_populate_defaults_with_existing_profiles(self, temporary_profiles_path):
        existing_profiles = ProfilesCollection(
            profiles=[Profile(name="existing", settings={SYNTASK_API_KEY: "test_key"})],
            active="existing",
        )
        save_profiles(existing_profiles)

        invoke_and_assert(
            ["profile", "populate-defaults"],
            user_input="y\ny",  # Confirm backup and update
            expected_output_contains=[
                "Proposed Changes:",
                "Add 'ephemeral'",
                "Add 'local'",
                "Add 'cloud'",
                f"Back up existing profiles to {temporary_profiles_path}.bak?",
                f"Update profiles at {temporary_profiles_path}?",
                f"Profiles updated in {temporary_profiles_path}",
            ],
        )

        new_profiles = load_profiles()
        assert {"local", "ephemeral", "cloud", "test", "existing"} == set(
            new_profiles.names
        )

        backup_profiles = _read_profiles_from(
            temporary_profiles_path.with_suffix(".toml.bak")
        )
        assert "existing" in backup_profiles.names
        assert backup_profiles["existing"].settings == {SYNTASK_API_KEY: "test_key"}

    def test_populate_defaults_no_changes_needed(self, temporary_profiles_path):
        shutil.copy(DEFAULT_PROFILES_PATH, temporary_profiles_path)

        invoke_and_assert(
            ["profile", "populate-defaults"],
            expected_output_contains=[
                "No changes needed. All profiles are up to date.",
            ],
            expected_code=0,
        )

        assert temporary_profiles_path.read_text() == DEFAULT_PROFILES_PATH.read_text()

    def test_show_profile_changes(self, capsys):
        default_profiles = ProfilesCollection(
            profiles=[
                Profile(
                    name="ephemeral",
                    settings={SYNTASK_API_URL: "https://api.syntask.khulnasoft.com"},
                ),
                Profile(
                    name="local", settings={SYNTASK_API_URL: "http://localhost:4200"}
                ),
                Profile(
                    name="cloud",
                    settings={SYNTASK_API_URL: "https://api.syntask.cloud"},
                ),
            ]
        )
        user_profiles = ProfilesCollection(
            profiles=[
                Profile(name="default", settings={SYNTASK_API_KEY: "test_key"}),
                Profile(name="custom", settings={SYNTASK_API_KEY: "custom_key"}),
            ]
        )

        changes = show_profile_changes(user_profiles, default_profiles)

        assert changes is True

        captured = capsys.readouterr()
        output = captured.out

        assert "Proposed Changes:" in output
        assert "Add 'ephemeral'" in output
        assert "Add 'local'" in output
        assert "Add 'cloud'" in output
