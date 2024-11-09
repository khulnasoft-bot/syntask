from typing import Any, Dict, Optional

from typing_extensions import Protocol

from syntask.client.cloud import get_cloud_client
from syntask.client.orchestration import ServerType, get_client


class CollectionsMetadataClient(Protocol):
    async def read_worker_metadata(self) -> Dict[str, Any]:
        ...

    async def __aenter__(self) -> "CollectionsMetadataClient":
        ...

    async def __aexit__(self, *exc_info) -> Any:
        ...


def get_collections_metadata_client(
    httpx_settings: Optional[Dict] = None,
) -> "CollectionsMetadataClient":
    """
    Creates a client that can be used to fetch metadata for
    Syntask collections.

    Will return a `CloudClient` if profile is set to connect
    to Syntask Cloud, otherwise will return an `OrchestrationClient`.
    """
    orchestration_client = get_client(httpx_settings=httpx_settings)
    if orchestration_client.server_type == ServerType.CLOUD:
        return get_cloud_client(httpx_settings=httpx_settings)
    else:
        return orchestration_client
