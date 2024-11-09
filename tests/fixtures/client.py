from typing import Dict

import pytest

from syntask import flow
from syntask.blocks.core import Block
from syntask.client.orchestration import SyntaskClient, get_client
from syntask.settings import SYNTASK_CLOUD_API_URL


@pytest.fixture
async def syntask_client(test_database_connection_url):
    async with get_client() as client:
        yield client


@pytest.fixture
async def cloud_client(syntask_client):
    async with SyntaskClient(SYNTASK_CLOUD_API_URL.value()) as cloud_client:
        yield cloud_client


@pytest.fixture(scope="session")
def flow_function():
    @flow(version="test", description="A test function")
    def client_test_flow(param=1):
        return param

    return client_test_flow


@pytest.fixture(scope="session")
def flow_function_dict_parameter():
    @flow(
        version="test", description="A test function with a dictionary as a parameter"
    )
    def client_test_flow_dict_parameter(dict_param: Dict[int, str]):
        return dict_param

    return client_test_flow_dict_parameter


@pytest.fixture(scope="session")
def test_block():
    class x(Block):
        _block_type_slug = "x-fixture"
        _logo_url = "https://en.wiktionary.org/wiki/File:LetterX.svg"
        _documentation_url = "https://en.wiktionary.org/wiki/X"
        foo: str

    return x
