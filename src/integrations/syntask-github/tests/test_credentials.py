import pytest
from sgqlc.endpoint.http import HTTPEndpoint
from syntask_github import GitHubCredentials


@pytest.mark.parametrize("token", [None, "token_value"])
def test_github_credentials_get_client(token):
    endpoint = GitHubCredentials(token=token).get_client()
    assert isinstance(endpoint, HTTPEndpoint)
    if token is not None:
        assert endpoint.base_headers == {"Authorization": "Bearer token_value"}
