import pytest

from syntask.deprecated.packaging import FilePackager
from syntask.deprecated.packaging.file import FilePackageManifest
from syntask.deprecated.packaging.serializers import (
    ImportSerializer,
    PickleSerializer,
    SourceSerializer,
)
from syntask.utilities.callables import parameter_schema

from . import howdy


@pytest.mark.parametrize(
    "Serializer", [SourceSerializer, ImportSerializer, PickleSerializer]
)
async def test_file_packager_by_serializer(Serializer):
    serializer = Serializer()
    packager = FilePackager(serializer=serializer)
    manifest = await packager.package(howdy)

    assert isinstance(manifest, FilePackageManifest)
    unpackaged_howdy = await manifest.unpackage()
    assert unpackaged_howdy("bro") == "howdy, bro!"


async def test_packager_sets_manifest_flow_parameter_schema():
    packager = FilePackager(serializer=SourceSerializer())
    manifest = await packager.package(howdy)
    assert manifest.flow_parameter_schema == parameter_schema(howdy.fn)
