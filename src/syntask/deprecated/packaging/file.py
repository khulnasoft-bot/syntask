"""
DEPRECATION WARNING:
This module is deprecated as of March 2024 and will not be available after September 2024.
"""

from uuid import UUID

from syntask._internal.compatibility.deprecated import deprecated_class
from syntask._internal.pydantic import HAS_PYDANTIC_V2

if HAS_PYDANTIC_V2:
    from pydantic.v1 import Field
else:
    from pydantic import Field

from typing_extensions import Literal

from syntask.blocks.core import Block
from syntask.client.orchestration import SyntaskClient
from syntask.client.utilities import inject_client
from syntask.deprecated.packaging.base import PackageManifest, Packager, Serializer
from syntask.deprecated.packaging.serializers import SourceSerializer
from syntask.filesystems import LocalFileSystem, ReadableFileSystem, WritableFileSystem
from syntask.flows import Flow
from syntask.settings import SYNTASK_HOME
from syntask.utilities.hashing import stable_hash


@deprecated_class(start_date="Mar 2024")
class FilePackageManifest(PackageManifest):
    """
    DEPRECATION WARNING:

    This class is deprecated as of version March 2024 and will not be available after September 2024.
    """

    type: str = "file"
    serializer: Serializer
    key: str
    filesystem_id: UUID

    @inject_client
    async def unpackage(self, client: SyntaskClient) -> Flow:
        block_document = await client.read_block_document(self.filesystem_id)
        filesystem: ReadableFileSystem = Block._from_block_document(block_document)
        content = await filesystem.read_path(self.key)
        return self.serializer.loads(content)


@deprecated_class(start_date="Mar 2024")
class FilePackager(Packager):
    """
    DEPRECATION WARNING:

    This class is deprecated as of version March 2024 and will not be available after September 2024.

    This packager stores the flow as a single file.

    By default, the file is the source code of the module the flow is defined in.
    Alternative serialization modes are available in `syntask.deprecated.packaging.serializers`.
    """

    type: Literal["file"] = "file"
    serializer: Serializer = Field(default_factory=SourceSerializer)
    filesystem: WritableFileSystem = Field(
        default_factory=lambda: LocalFileSystem(
            basepath=SYNTASK_HOME.value() / "storage"
        )
    )

    @inject_client
    async def package(self, flow: Flow, client: "SyntaskClient") -> FilePackageManifest:
        content = self.serializer.dumps(flow)
        key = stable_hash(content)

        await self.filesystem.write_path(key, content)

        filesystem_id = (
            self.filesystem._block_document_id
            or await self.filesystem._save(is_anonymous=True)
        )

        return FilePackageManifest(
            **{
                **self.base_manifest(flow).dict(),
                **{
                    "serializer": self.serializer,
                    "filesystem_id": filesystem_id,
                    "key": key,
                },
            }
        )
