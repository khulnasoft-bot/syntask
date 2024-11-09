import shutil
import sys
from pathlib import Path

import pytest
import yaml

import syntask
from syntask.deployments.base import (
    _find_flow_functions_in_file,
    _search_for_flow_functions,
    configure_project_by_recipe,
    initialize_project,
)
from syntask.settings import SYNTASK_DEBUG_MODE, temporary_settings
from syntask.utilities.asyncutils import run_sync_in_worker_thread
from syntask.utilities.filesystem import tmpchdir

TEST_PROJECTS_DIR = syntask.__development_base_path__ / "tests" / "test-projects"


@pytest.fixture(autouse=True)
def project_dir(tmp_path):
    with tmpchdir(tmp_path):
        if sys.version_info >= (3, 8):
            shutil.copytree(TEST_PROJECTS_DIR, tmp_path, dirs_exist_ok=True)
            (tmp_path / ".syntask").mkdir(exist_ok=True, mode=0o0700)
            yield tmp_path
        else:
            shutil.copytree(TEST_PROJECTS_DIR, tmp_path / "three-seven")
            (tmp_path / "three-seven" / ".syntask").mkdir(exist_ok=True, mode=0o0700)
            yield tmp_path / "three-seven"


class TestRecipes:
    async def test_configure_project_by_recipe_raises(self):
        with pytest.raises(ValueError, match="Unknown recipe"):
            configure_project_by_recipe("not-a-recipe")

    @pytest.mark.parametrize(
        "recipe",
        [
            d.absolute().name
            for d in Path(
                syntask.__development_base_path__
                / "src"
                / "syntask"
                / "deployments"
                / "recipes"
            ).iterdir()
            if d.is_dir()
        ],
    )
    async def test_configure_project_by_recipe_doesnt_raise(self, recipe):
        recipe_config = configure_project_by_recipe(recipe)
        for key in ["name", "syntask-version", "build", "push", "pull"]:
            assert key in recipe_config

    @pytest.mark.parametrize(
        "recipe",
        [
            d.absolute().name
            for d in Path(
                syntask.__development_base_path__
                / "src"
                / "syntask"
                / "deployments"
                / "recipes"
            ).iterdir()
            if d.is_dir() and "git" in d.absolute().name
        ],
    )
    async def test_configure_project_handles_templates_on_git_recipes(self, recipe):
        recipe_config = configure_project_by_recipe(
            recipe, repository="test-org/test-repo"
        )
        clone_step = recipe_config["pull"][0]["syntask.deployments.steps.git_clone"]
        assert clone_step["repository"] == "test-org/test-repo"
        assert clone_step["branch"] == "{{ branch }}"

    async def test_configure_project_replaces_templates_on_docker(self):
        recipe_config = configure_project_by_recipe("docker", name="test-dir")
        clone_step = recipe_config["pull"][0][
            "syntask.deployments.steps.set_working_directory"
        ]
        assert clone_step["directory"] == "/opt/syntask/test-dir"


class TestInitProject:
    async def test_initialize_project_works(self):
        files = initialize_project()
        assert len(files) >= 2

        for file in files:
            assert Path(file).exists()

        # test defaults
        with open("syntask.yaml", "r") as f:
            contents = yaml.safe_load(f)

        assert contents["name"] is not None
        assert contents["syntask-version"] == syntask.__version__

    async def test_initialize_project_with_name(self):
        files = initialize_project(name="my-test-its-a-test")
        assert len(files) >= 2

        with open("syntask.yaml", "r") as f:
            contents = yaml.safe_load(f)

        assert contents["name"] == "my-test-its-a-test"

    async def test_initialize_project_with_recipe(self):
        files = initialize_project(recipe="docker-git")
        assert len(files) >= 2

        with open("syntask.yaml", "r") as f:
            contents = yaml.safe_load(f)

        clone_step = contents["pull"][0]
        assert "syntask.deployments.steps.git_clone" in clone_step

        build_step = contents["build"][0]
        assert "syntask_docker.deployments.steps.build_docker_image" in build_step

    @pytest.mark.parametrize(
        "recipe",
        [
            d.absolute().name
            for d in Path(
                syntask.__development_base_path__
                / "src"
                / "syntask"
                / "deployments"
                / "recipes"
            ).iterdir()
            if d.is_dir() and "docker" in d.absolute().name
        ],
    )
    async def test_initialize_project_with_docker_recipe_default_image(self, recipe):
        files = initialize_project(recipe=recipe)
        assert len(files) >= 2

        with open("syntask.yaml", "r") as f:
            contents = yaml.safe_load(f)

        build_step = contents["build"][0]
        assert "syntask_docker.deployments.steps.build_docker_image" in build_step

        assert (
            contents["deployments"][0]["work_pool"]["job_variables"]["image"]
            == "{{ build_image.image }}"
        )


class TestDiscoverFlows:
    async def test_find_all_flows_in_dir_tree(self, project_dir):
        flows = await _search_for_flow_functions(str(project_dir))
        assert len(flows) == 6, f"Expected 6 flows, found {len(flows)}"

        expected_flows = [
            {
                "flow_name": "foobar",
                "function_name": "foobar",
                "filepath": str(
                    project_dir / "nested-project" / "implicit_relative.py"
                ),
            },
            {
                "flow_name": "foobar",
                "function_name": "foobar",
                "filepath": str(
                    project_dir / "nested-project" / "explicit_relative.py"
                ),
            },
            {
                "flow_name": "my_flow",
                "function_name": "my_flow",
                "filepath": str(project_dir / "flows" / "hello.py"),
            },
            {
                "flow_name": "my_flow2",
                "function_name": "my_flow2",
                "filepath": str(project_dir / "flows" / "hello.py"),
            },
            {
                "flow_name": "prod_flow",
                "function_name": "prod_flow",
                "filepath": str(
                    project_dir / "import-project" / "my_module" / "flow.py"
                ),
            },
            {
                "flow_name": "test_flow",
                "function_name": "test_flow",
                "filepath": str(
                    project_dir / "import-project" / "my_module" / "flow.py"
                ),
            },
        ]

        for flow in flows:
            assert flow in expected_flows, f"Unexpected flow: {flow}"
            expected_flows.remove(flow)

        assert len(expected_flows) == 0, f"Missing flows: {expected_flows}"

    async def test_find_all_flows_works_on_large_directory_structures(self):
        flows = await _search_for_flow_functions(str(syntask.__development_base_path__))
        assert len(flows) > 500

    async def test_find_flow_functions_in_file_returns_empty_list_on_file_error(
        self, caplog
    ):
        with temporary_settings({SYNTASK_DEBUG_MODE: True}):
            assert await _find_flow_functions_in_file("foo.py") == []
            assert "Could not open foo.py" in caplog.text

    async def test_syntask_can_be_imported_from_non_main_thread(self):
        """testing due to `asyncio.Semaphore` error when importing syntask from a worker thread
        in python <= 3.9
        """

        def import_syntask():
            import syntask  # noqa: F401

        await run_sync_in_worker_thread(import_syntask)
