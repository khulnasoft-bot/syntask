"""Module containing docker credentials."""

import docker
from pydantic import Field, SecretStr

from syntask.blocks.core import Block
from syntask.logging import get_run_logger
from syntask.utilities.asyncutils import run_sync_in_worker_thread


class DockerRegistryCredentials(Block):
    """
    Block used to manage credentials for interacting with a Docker Registry.

    Examples:
        Log into Docker Registry.
        ```python
        from syntask_docker import DockerHost, DockerRegistryCredentials

        docker_host = DockerHost()
        docker_registry_credentials = DockerRegistryCredentials(
            username="my_username",
            password="my_password",
            registry_url="registry.hub.docker.com",
        )
        with docker_host.get_client() as client:
            docker_registry_credentials.login(client)
        ```
    """

    _block_type_name = "Docker Registry Credentials"
    _logo_url = "https://cdn.sanity.io/images/3ugk85nk/production/14a315b79990200db7341e42553e23650b34bb96-250x250.png"  # noqa
    _description = "Store credentials for interacting with a Docker Registry."

    username: str = Field(
        default=..., description="The username to log into the registry with."
    )
    password: SecretStr = Field(
        default=..., description="The password to log into the registry with."
    )
    registry_url: str = Field(
        default=...,
        description=(
            'The URL to the registry. Generally, "http" or "https" can be omitted.'
        ),
        examples=["index.docker.io"],
    )
    reauth: bool = Field(
        default=True,
        description="Whether or not to reauthenticate on each interaction.",
    )

    async def login(self, client: docker.DockerClient):
        """
        Authenticates a given Docker client with the configured Docker registry.

        Args:
            client: A Docker Client.
        """
        logger = get_run_logger()
        logger.debug(f"Logging into {self.registry_url}.")
        await run_sync_in_worker_thread(
            client.login,
            username=self.username,
            password=self.password.get_secret_value(),
            registry=self.registry_url,
            # See https://github.com/docker/docker-py/issues/2256 for information on
            # the default value for reauth.
            reauth=self.reauth,
        )
