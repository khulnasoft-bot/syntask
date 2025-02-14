import shutil
import subprocess
import sys
import warnings
from pathlib import Path
from textwrap import dedent
from typing import Optional
from unittest.mock import ANY, call

import pytest

from syntask._internal.compatibility.deprecated import SyntaskDeprecationWarning
from syntask.blocks.core import Block
from syntask.blocks.system import Secret
from syntask.client.orchestration import SyntaskClient
from syntask.deployments.steps import run_step
from syntask.deployments.steps.core import StepExecutionError, run_steps
from syntask.deployments.steps.utility import run_shell_script
from syntask.testing.utilities import AsyncMock, MagicMock
from syntask.utilities.filesystem import tmpchdir


@pytest.fixture
async def variables(syntask_client: SyntaskClient):
    await syntask_client._client.post(
        "/variables/", json={"name": "test_variable_1", "value": "test_value_1"}
    )
    await syntask_client._client.post(
        "/variables/", json={"name": "test_variable_2", "value": "test_value_2"}
    )


@pytest.fixture(scope="session")
def set_dummy_env_var():
    import os

    os.environ["DUMMY_ENV_VAR"] = "dummy"


class TestRunStep:
    async def test_run_step_runs_importable_functions(self):
        output = await run_step(
            {
                "syntask.deployments.steps.run_shell_script": {
                    "script": "echo 'this is a test'",
                }
            },
        )
        assert isinstance(output, dict)
        assert output == {
            "stdout": "this is a test",
            "stderr": "",
        }

    async def test_run_step_errors_with_improper_format(self):
        with pytest.raises(ValueError, match="unexpected"):
            await run_step(
                {
                    "syntask.deployments.steps.run_shell_script": {
                        "script": "echo 'this is a test'"
                    },
                    "jedi": 0,
                }
            )

    async def test_run_step_resolves_block_document_references_before_running(self):
        await Secret(value="echo 'I am a secret!'").save(name="test-secret")

        output = await run_step(
            {
                "syntask.deployments.steps.run_shell_script": {
                    "script": "{{ syntask.blocks.secret.test-secret }}",
                }
            }
        )
        assert isinstance(output, dict)
        assert output == {
            "stdout": "I am a secret!",
            "stderr": "",
        }

    async def test_run_step_resolves_environment_variables_before_running(
        self, monkeypatch
    ):
        monkeypatch.setenv("TEST_ENV_VAR", "test_value")
        output = await run_step(
            {
                "syntask.deployments.steps.run_shell_script": {
                    "script": 'echo "{{ $TEST_ENV_VAR }}"',
                }
            }
        )
        assert isinstance(output, dict)
        assert output == {
            "stdout": "test_value",
            "stderr": "",
        }

    async def test_run_step_resolves_variables_before_running(self, variables):
        output = await run_step(
            {
                "syntask.deployments.steps.run_shell_script": {
                    "script": (
                        "echo '{{ syntask.variables.test_variable_1 }}:{{"
                        " syntask.variables.test_variable_2 }}'"
                    ),
                }
            }
        )
        assert isinstance(output, dict)
        assert output == {
            "stdout": "test_value_1:test_value_2",
            "stderr": "",
        }

    async def test_run_step_runs_async_functions(self):
        output = await run_step(
            {
                "anyio.run_process": {
                    "command": ["echo", "hello world"],
                }
            }
        )
        assert output.returncode == 0
        assert output.stdout.decode().strip() == "hello world"

    async def test_requirement_installation_successful(self, monkeypatch):
        """
        Test that the function attempts to install the package and succeeds.
        """
        import_module_mock = MagicMock()
        monkeypatch.setattr(
            "syntask.deployments.steps.core.import_module", import_module_mock
        )

        monkeypatch.setattr(subprocess, "check_call", MagicMock())

        import_object_mock = MagicMock(side_effect=[ImportError, lambda x: x])
        monkeypatch.setattr(
            "syntask.deployments.steps.core.import_object", import_object_mock
        )

        await run_step(
            {"test_module.test_function": {"requires": "test-package>=1.0.0", "x": 1}}
        )

        import_module_mock.assert_called_once_with("test_package")
        assert (
            import_object_mock.call_count == 2
        )  # once before and once after installation
        subprocess.check_call.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "test-package>=1.0.0"]
        )

    @pytest.mark.parametrize(
        "package,expected",
        [
            ("prefect-aws", "syntask[aws]"),
            ("syntask-gcp", "syntask[gcp]"),
            ("syntask-azure", "syntask[azure]"),
            ("prefect-docker", "syntask[docker]"),
            ("syntask-kubernetes", "syntask[kubernetes]"),
        ],
    )
    async def test_requirement_installation_uses_syntask_extras(
        self, monkeypatch, package, expected
    ):
        import_module_mock = MagicMock()
        monkeypatch.setattr(
            "syntask.deployments.steps.core.import_module", import_module_mock
        )

        monkeypatch.setattr(subprocess, "check_call", MagicMock())

        import_object_mock = MagicMock(side_effect=[ImportError, lambda x: x])
        monkeypatch.setattr(
            "syntask.deployments.steps.core.import_object", import_object_mock
        )

        await run_step({"test_module.test_function": {"requires": package, "x": 1}})

        import_module_mock.assert_called_once_with(package.replace("-", "_"))
        assert (
            import_object_mock.call_count == 2
        )  # once before and once after installation
        subprocess.check_call.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", expected]
        )

    async def test_install_multiple_requirements(self, monkeypatch):
        """
        Test that passing multiple requirements installs all of them.
        """
        import_module_mock = MagicMock(side_effect=[None, ImportError])
        monkeypatch.setattr(
            "syntask.deployments.steps.core.import_module", import_module_mock
        )

        monkeypatch.setattr(subprocess, "check_call", MagicMock())

        import_object_mock = MagicMock(side_effect=[lambda x: x])
        monkeypatch.setattr(
            "syntask.deployments.steps.core.import_object", import_object_mock
        )

        await run_step(
            {
                "test_module.test_function": {
                    "requires": ["test-package>=1.0.0", "another"],
                    "x": 1,
                }
            }
        )

        import_module_mock.assert_has_calls([call("test_package"), call("another")])
        subprocess.check_call.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "test-package>=1.0.0", "another"]
        )

    async def test_requirement_installation_failure(self, monkeypatch, caplog):
        """
        Test that the function logs a warning if it fails to install the package.
        """
        # Mocking the import_module function to always raise ImportError
        monkeypatch.setattr(
            "syntask.deployments.steps.core.import_module",
            MagicMock(side_effect=ImportError),
        )

        # Mock subprocess.check_call to simulate failed package installation
        monkeypatch.setattr(
            subprocess,
            "check_call",
            MagicMock(side_effect=subprocess.CalledProcessError(1, ["pip"])),
        )

        with pytest.raises(ImportError):
            await run_step(
                {
                    "test_module.test_function": {
                        "requires": "nonexistent-package>=1.0.0"
                    }
                }
            )

        assert subprocess.check_call.called
        record = next(
            (
                record
                for record in caplog.records
                if "Unable to install required packages" in record.message
            ),
            None,
        )
        assert record is not None, "No warning was logged"
        assert record.levelname == "WARNING"


class TestRunSteps:
    async def test_run_steps_runs_multiple_steps(self):
        steps = [
            {
                "syntask.deployments.steps.run_shell_script": {
                    "script": "echo 'this is a test'",
                    "id": "why_not_to_panic",
                }
            },
            {
                "syntask.deployments.steps.run_shell_script": {
                    "script": r"echo Don\'t Panic: {{ why_not_to_panic.stdout }}"
                }
            },
        ]
        step_outputs = await run_steps(steps, {})
        assert step_outputs == {
            "why_not_to_panic": {
                "stdout": "this is a test",
                "stderr": "",
            },
            "stdout": "Don't Panic: this is a test",
            "stderr": "",
        }

    async def test_run_steps_handles_error_gracefully(self, variables):
        steps = [
            {
                "syntask.deployments.steps.run_shell_script": {
                    "script": "echo 'this is a test'",
                    "id": "why_not_to_panic",
                }
            },
            {
                "nonexistent.module": {
                    "__fn": lambda x: x * 2,
                    "value": "{{ step_output_1 }}",
                }
            },
        ]
        with pytest.raises(StepExecutionError, match="nonexistent.module"):
            await run_steps(steps, {})

    async def test_run_steps_prints_step_names(
        self,
    ):
        mock_print = MagicMock()
        steps = [
            {
                "syntask.deployments.steps.run_shell_script": {
                    "script": "echo 'this is a test'",
                    "id": "why_not_to_panic",
                }
            },
            {
                "syntask.deployments.steps.run_shell_script": {
                    "script": (
                        'bash -c echo "Don\'t Panic: {{ why_not_to_panic.stdout }}"'
                    )
                }
            },
        ]
        await run_steps(steps, {}, print_function=mock_print)
        mock_print.assert_any_call(" > Running run_shell_script step...")

    async def test_run_steps_prints_deprecation_warnings(self, monkeypatch):
        def func(*args, **kwargs):
            warnings.warn("this is a warning", DeprecationWarning)
            return {}

        monkeypatch.setattr("syntask.deployments.steps.run_shell_script", func)

        mock_print = MagicMock()
        steps = [
            {
                "syntask.deployments.steps.run_shell_script": {
                    "script": "echo 'this is a test'",
                    "id": "why_not_to_panic",
                }
            },
        ]
        await run_steps(steps, {}, print_function=mock_print)
        mock_print.assert_any_call("this is a warning", style="yellow")

    async def test_run_steps_prints_syntask_deprecation_warnings(self, monkeypatch):
        def func(*args, **kwargs):
            warnings.warn("this is a warning", SyntaskDeprecationWarning)
            return {}

        monkeypatch.setattr("syntask.deployments.steps.run_shell_script", func)

        mock_print = MagicMock()
        steps = [
            {
                "syntask.deployments.steps.run_shell_script": {
                    "script": "echo 'this is a test'",
                    "id": "why_not_to_panic",
                }
            },
        ]
        await run_steps(steps, {}, print_function=mock_print)
        mock_print.assert_any_call("this is a warning", style="yellow")

    async def test_run_steps_can_print_warnings_without_style(self, monkeypatch):
        def func(*args, **kwargs):
            warnings.warn("this is a warning", SyntaskDeprecationWarning)
            return {}

        monkeypatch.setattr("syntask.deployments.steps.run_shell_script", func)

        # raise an exception when style is passed. exception type is irrelevant
        mock_print = MagicMock(
            side_effect=lambda *args, **kwargs: 1 / 0 if kwargs.get("style") else None
        )
        steps = [
            {
                "syntask.deployments.steps.run_shell_script": {
                    "script": "echo 'this is a test'",
                    "id": "why_not_to_panic",
                }
            },
        ]
        await run_steps(steps, {}, print_function=mock_print)
        mock_print.assert_any_call("this is a warning")


class MockCredentials:
    def __init__(
        self, token: str, username: Optional[str] = None, password: Optional[str] = None
    ):
        self.token = token
        self.username = username
        self.password = password

        self.data = {
            "value": {
                "token": self.token,
                "username": self.username,
                "password": self.password,
            }
        }

    async def save(self, name: str):
        pass

    async def load(self, name: str):
        return MockCredentials(token="mock-token")


@pytest.fixture
def git_repository_mock(monkeypatch):
    git_repository_mock = MagicMock()
    pull_code_mock = AsyncMock()
    git_repository_mock.return_value.pull_code = pull_code_mock
    git_repository_mock.return_value.destination = Path.cwd() / "repo"
    monkeypatch.setattr(
        "syntask.deployments.steps.pull.GitRepository",
        git_repository_mock,
    )
    return git_repository_mock


class TestGitCloneStep:
    async def test_git_clone(self, git_repository_mock):
        output = await run_step(
            {
                "syntask.deployments.steps.git_clone": {
                    "repository": "https://github.com/org/repo.git",
                }
            }
        )
        assert output["directory"] == "repo"
        git_repository_mock.assert_called_once_with(
            url="https://github.com/org/repo.git",
            credentials=None,
            branch=None,
            include_submodules=False,
        )
        git_repository_mock.return_value.pull_code.assert_awaited_once()

    async def test_git_clone_include_submodules(self, git_repository_mock):
        output = await run_step(
            {
                "syntask.deployments.steps.git_clone": {
                    "repository": "https://github.com/org/has-submodules.git",
                    "include_submodules": True,
                }
            }
        )
        assert output["directory"] == "repo"
        git_repository_mock.assert_called_once_with(
            url="https://github.com/org/has-submodules.git",
            credentials=None,
            branch=None,
            include_submodules=True,
        )
        git_repository_mock.return_value.pull_code.assert_awaited_once()

    async def test_git_clone_with_access_token(self, git_repository_mock):
        await Secret(value="my-access-token").save(name="my-access-token")
        await run_step(
            {
                "syntask.deployments.steps.git_clone": {
                    "repository": "https://github.com/org/repo.git",
                    "access_token": "{{ syntask.blocks.secret.my-access-token }}",
                }
            }
        )
        git_repository_mock.assert_called_once_with(
            url="https://github.com/org/repo.git",
            credentials={"access_token": "my-access-token"},
            branch=None,
            include_submodules=False,
        )
        git_repository_mock.return_value.pull_code.assert_awaited_once()

    async def test_git_clone_with_credentials(self, git_repository_mock):
        class MockGitCredentials(Block):
            username: str
            password: str

        await MockGitCredentials(username="marvin42", password="hunter2").save(
            name="my-credentials"
        )
        await run_step(
            {
                "syntask.deployments.steps.git_clone": {
                    "repository": "https://github.com/org/repo.git",
                    "credentials": (
                        "{{ syntask.blocks.mockgitcredentials.my-credentials }}"
                    ),
                }
            }
        )
        git_repository_mock.assert_called_once_with(
            url="https://github.com/org/repo.git",
            credentials={"username": "marvin42", "password": "hunter2"},
            branch=None,
            include_submodules=False,
        )
        git_repository_mock.return_value.pull_code.assert_awaited_once()

    async def test_git_clone_retry(self, monkeypatch, caplog):
        mock_git_repo = MagicMock()
        mock_git_repo.return_value.pull_code = AsyncMock(
            side_effect=[
                RuntimeError("Octocat went out to lunch"),
                RuntimeError("Octocat is playing chess in the break room"),
                None,  # Successful on third attempt
            ]
        )
        mock_git_repo.return_value.destination.relative_to.return_value = "repo"
        monkeypatch.setattr(
            "syntask.deployments.steps.pull.GitRepository", mock_git_repo
        )

        async def mock_sleep(seconds):
            pass

        monkeypatch.setattr("asyncio.sleep", mock_sleep)

        with caplog.at_level("WARNING"):
            result = await run_step(
                {
                    "syntask.deployments.steps.git_clone": {
                        "repository": "https://github.com/org/repo.git"
                    }
                }
            )

        assert (
            "Attempt 1 of function 'git_clone' failed with RuntimeError. Retrying in "
            in caplog.text
        )
        assert (
            "Attempt 2 of function 'git_clone' failed with RuntimeError. Retrying in "
            in caplog.text
        )

        assert result == {"directory": "repo"}

        expected_call = call(
            url="https://github.com/org/repo.git",
            credentials=None,
            branch=None,
            include_submodules=False,
        )

        assert mock_git_repo.call_args_list == [expected_call] * 3


class TestPullFromRemoteStorage:
    @pytest.fixture
    def remote_storage_mock(self, monkeypatch):
        remote_storage_mock = MagicMock()
        pull_code_mock = AsyncMock()
        remote_storage_mock.return_value.pull_code = pull_code_mock
        remote_storage_mock.return_value.destination = Path.cwd() / "bucket" / "folder"
        monkeypatch.setattr(
            "syntask.deployments.steps.pull.RemoteStorage",
            remote_storage_mock,
        )
        return remote_storage_mock

    @pytest.fixture
    def subprocess_mock(self, monkeypatch):
        subprocess_mock = MagicMock()
        monkeypatch.setattr(
            "syntask.deployments.steps.core.subprocess",
            subprocess_mock,
        )
        return subprocess_mock

    @pytest.fixture
    def import_module_mock(self, monkeypatch):
        import_module_mock = MagicMock(side_effect=ImportError())
        monkeypatch.setattr(
            "syntask.deployments.steps.core.import_module",
            import_module_mock,
        )
        return import_module_mock

    async def test_pull_from_remote_storage(
        self, remote_storage_mock, subprocess_mock, import_module_mock
    ):
        output = await run_step(
            {
                "syntask.deployments.steps.pull_from_remote_storage": {
                    "requires": "s3fs<3.0",
                    "url": "s3://bucket/folder",
                    "key": "my-access-key-id",
                    "secret": "my-secret-access-key",
                }
            }
        )
        assert output["directory"] == "bucket/folder"
        import_module_mock.assert_called_once_with("s3fs")
        subprocess_mock.check_call.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "s3fs<3.0"]
        )
        remote_storage_mock.assert_called_once_with(
            "s3://bucket/folder",
            key="my-access-key-id",
            secret="my-secret-access-key",
        )
        remote_storage_mock.return_value.pull_code.assert_awaited_once()


class TestRunShellScript:
    async def test_run_shell_script_single_command(self, capsys):
        result = await run_shell_script("echo Hello World", stream_output=True)
        assert result["stdout"] == "Hello World"
        assert result["stderr"] == ""

        # Validate the output was streamed to the console
        out, err = capsys.readouterr()
        assert out.strip() == "Hello World"
        assert err == ""

    async def test_run_shell_script_multiple_commands(self, capsys):
        script = """
        echo First Line
        echo Second Line
        """
        result = await run_shell_script(script, stream_output=True)
        assert result["stdout"] == "First Line\nSecond Line"
        assert result["stderr"] == ""

        # Validate the output was streamed to the console
        out, err = capsys.readouterr()
        assert out.strip() == "First Line\nSecond Line"
        assert err == ""

    @pytest.mark.skipif(
        sys.platform == "win32", reason="stderr redirect does not work on Windows"
    )
    async def test_run_shell_script_stderr(self, capsys):
        script = "bash -c '>&2 echo Error Message'"
        result = await run_shell_script(script, stream_output=True)
        assert result["stdout"] == ""
        assert result["stderr"] == "Error Message"

        # Validate the error was streamed to the console
        out, err = capsys.readouterr()
        assert out == ""
        assert err.strip() == "Error Message"

    @pytest.mark.parametrize(
        "script,expected",
        [
            ("bash -c 'echo $TEST_ENV_VAR'", "Test Value"),
            ("echo $TEST_ENV_VAR", "$TEST_ENV_VAR"),
        ],
    )
    async def test_run_shell_script_with_env(self, script, expected, capsys):
        result = await run_shell_script(
            script, env={"TEST_ENV_VAR": "Test Value"}, stream_output=True
        )
        assert result["stdout"] == expected
        assert result["stderr"] == ""

        # Validate the output was streamed to the console
        out, err = capsys.readouterr()
        assert out.strip() == expected
        assert err == ""

    @pytest.mark.parametrize(
        "script",
        [
            "echo $DUMMY_ENV_VAR",
            "bash -c 'echo $DUMMY_ENV_VAR'",
        ],
    )
    async def test_run_shell_script_expand_env(self, script, capsys, set_dummy_env_var):
        result = await run_shell_script(
            script,
            expand_env_vars=True,
            stream_output=True,
        )

        assert result["stdout"] == "dummy"
        assert result["stderr"] == ""

    async def test_run_shell_script_no_expand_env(self, capsys, set_dummy_env_var):
        result = await run_shell_script(
            "echo $DUMMY_ENV_VAR",
            stream_output=True,
        )

        assert result["stdout"] == "$DUMMY_ENV_VAR"
        assert result["stderr"] == ""

    async def test_run_shell_script_no_output(self, capsys):
        result = await run_shell_script("echo Hello World", stream_output=False)
        assert result["stdout"] == "Hello World"
        assert result["stderr"] == ""

        # Validate nothing was streamed to the console
        out, err = capsys.readouterr()
        assert out == ""
        assert err == ""

    async def test_run_shell_script_in_directory(self):
        parent_dir = str(Path.cwd().parent)
        result = await run_shell_script(
            "pwd", directory=parent_dir, stream_output=False
        )
        assert result["stdout"] == parent_dir
        assert result["stderr"] == ""

    @pytest.mark.skipif(
        sys.platform != "win32",
        reason="_open_anyio_process errors when mocking OS in test context",
    )
    async def test_run_shell_script_split_on_windows(self, monkeypatch):
        # return type needs to be mocked to avoid TypeError
        shex_split_mock = MagicMock(return_value=["echo", "Hello", "World"])
        monkeypatch.setattr(
            "syntask.deployments.steps.utility.shlex.split",
            shex_split_mock,
        )
        result = await run_shell_script("echo Hello World")
        # validates that command is parsed as non-posix
        shex_split_mock.assert_called_once_with("echo Hello World", posix=False)
        assert result["stdout"] == "Hello World"
        assert result["stderr"] == ""


class MockProcess:
    def __init__(self, returncode=0):
        self.returncode = returncode

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def wait(self):
        pass


class TestPipInstallRequirements:
    async def test_pip_install_reqs_runs_expected_command(self, monkeypatch):
        open_process_mock = MagicMock(return_value=MockProcess(0))
        monkeypatch.setattr(
            "syntask.deployments.steps.utility.open_process",
            open_process_mock,
        )

        mock_stream_capture = AsyncMock()

        monkeypatch.setattr(
            "syntask.deployments.steps.utility._stream_capture_process_output",
            mock_stream_capture,
        )

        await run_step(
            {
                "syntask.deployments.steps.pip_install_requirements": {
                    "id": "pip-install-step"
                }
            }
        )

        open_process_mock.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            cwd=None,
            stderr=ANY,
            stdout=ANY,
        )

    async def test_pip_install_reqs_custom_requirements_file(self, monkeypatch):
        open_process_mock = MagicMock(return_value=MockProcess(0))
        monkeypatch.setattr(
            "syntask.deployments.steps.utility.open_process",
            open_process_mock,
        )

        mock_stream_capture = AsyncMock()

        monkeypatch.setattr(
            "syntask.deployments.steps.utility._stream_capture_process_output",
            mock_stream_capture,
        )

        await run_step(
            {
                "syntask.deployments.steps.pip_install_requirements": {
                    "id": "pip-install-step",
                    "requirements_file": "dev-requirements.txt",
                }
            }
        )

        open_process_mock.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "-r", "dev-requirements.txt"],
            cwd=None,
            stderr=ANY,
            stdout=ANY,
        )

    async def test_pip_install_reqs_with_directory_step_output_succeeds(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ):
        open_process_mock = MagicMock(return_value=MockProcess(0))
        monkeypatch.setattr(
            "syntask.deployments.steps.utility.open_process",
            open_process_mock,
        )

        mock_stream_capture = AsyncMock()

        monkeypatch.setattr(
            "syntask.deployments.steps.utility._stream_capture_process_output",
            mock_stream_capture,
        )

        steps = [
            {
                "syntask.deployments.steps.git_clone": {
                    "id": "clone-step",
                    "repository": "https://github.com/SynoPKG/hello-projects.git",
                }
            },
            {
                "syntask.deployments.steps.pip_install_requirements": {
                    "id": "pip-install-step",
                    "directory": "{{ clone-step.directory }}",
                    "requirements_file": "requirements.txt",
                }
            },
        ]

        step_outputs = {
            "clone-step": {"directory": "hello-projects"},
            "directory": "hello-projects",
            "pip-install-step": {"stdout": "", "stderr": ""},
            "stdout": "",
            "stderr": "",
        }

        open_process_mock.run.return_value = MagicMock(**step_outputs)

        with tmpchdir(tmp_path):
            output = await run_steps(steps)

        assert output == step_outputs

        open_process_mock.assert_called_once_with(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                "requirements.txt",
            ],
            cwd="hello-projects",
            stderr=ANY,
            stdout=ANY,
        )

    async def test_pip_install_fails_on_error(self):
        with pytest.raises(RuntimeError) as exc:
            await run_step(
                {
                    "syntask.deployments.steps.pip_install_requirements": {
                        "id": "pip-install-step",
                        "requirements_file": "doesnt-exist.txt",
                    }
                }
            )
        assert (
            "pip_install_requirements failed with error code 1: ERROR: Could not open "
            "requirements file: [Errno 2] No such file or directory: "
            "'doesnt-exist.txt'" in str(exc.value)
        )


class TestPullWithBlock:
    @pytest.fixture
    async def test_block(self, monkeypatch, tmp_path):
        monkeypatch.chdir(str(tmp_path))  # ensures never writes to active directory

        class FakeStorageBlock(Block):
            _block_type_slug = "fake-storage-block"

            code: str = dedent(
                """\
                from syntask import flow

                @flow
                def test_flow():
                    return 1
                """
            )

            async def get_directory(self, local_path: str):
                (Path(local_path) / "flows.py").write_text(self.code)

        block = FakeStorageBlock()
        await block.save("test-block")
        return block

    async def test_normal_operation(self, test_block: Block):
        """
        A block type slug and a block document name corresponding
        to a block with the get_directory method can be used
        to pull code into the current working path.
        """
        try:
            output = await run_step(
                {
                    "syntask.deployments.steps.pull_with_block": {
                        "block_type_slug": test_block.get_block_type_slug(),
                        "block_document_name": test_block._block_document_name,
                    }
                }
            )
            assert "directory" in output
            assert Path(f"{output['directory']}/flows.py").read_text() == dedent(
                """\
                from syntask import flow

                @flow
                def test_flow():
                    return 1
                """
            )
        finally:
            if "output" in locals() and "directory" in output:
                shutil.rmtree(f"{output['directory']}")

    async def test_block_not_found(self, caplog):
        """
        When a `pull_with_block` step is run with a block type slug
        and block document name that can't be resolved, `run_step`
        should raise and log a message.
        """
        with pytest.raises(ValueError):
            await run_step(
                {
                    "syntask.deployments.steps.pull_with_block": {
                        "block_type_slug": "in-the",
                        "block_document_name": "wind",
                    }
                }
            )

        assert "Unable to load block 'in-the/wind'" in caplog.text

    async def test_incorrect_type_of_block(self, caplog):
        """
        When a `pull_with_block` step is run with a block that doesn't
        have a `get_directory` method, `run_step` should raise and log
        a message.
        """

        class Wrong(Block):
            square_peg: str = "round_hole"

        block = Wrong()
        await block.save("test-block")

        with pytest.raises(ValueError):
            await run_step(
                {
                    "syntask.deployments.steps.pull_with_block": {
                        "block_type_slug": block.get_block_type_slug(),
                        "block_document_name": block._block_document_name,
                    }
                }
            )

        assert (
            "Unable to create storage adapter for block"
            f" '{block.get_block_type_slug()}/{block._block_document_name}"
            in caplog.text
        )
