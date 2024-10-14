import sys
from typing import Optional

import pytest

from syntask import __version_info__
from syntask.utilities.dockerutils import get_syntask_image_name

COMMIT_SHA = __version_info__["full-revisionid"][:7]
PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"


@pytest.mark.parametrize(
    "syntask_version, python_version, flavor, expected",
    [
        (
            None,
            None,
            None,
            f"synopkg/syntask-dev:sha-{COMMIT_SHA}-python{PYTHON_VERSION}",
        ),
        (None, "3.9", None, f"synopkg/syntask-dev:sha-{COMMIT_SHA}-python3.9"),
        (None, "3.10", None, f"synopkg/syntask-dev:sha-{COMMIT_SHA}-python3.10"),
        (None, "3.11", None, f"synopkg/syntask-dev:sha-{COMMIT_SHA}-python3.11"),
        (None, "3.12", None, f"synopkg/syntask-dev:sha-{COMMIT_SHA}-python3.12"),
        (
            None,
            None,
            "conda",
            f"synopkg/syntask-dev:sha-{COMMIT_SHA}-python{PYTHON_VERSION}-conda",
        ),
        ("3.0.0", None, None, f"synopkg/syntask:3.0.0-python{PYTHON_VERSION}"),
        (
            "3.0.0.post0.dev1",
            None,
            None,
            f"synopkg/syntask-dev:sha-{COMMIT_SHA}-python{PYTHON_VERSION}",
        ),
    ],
)
def test_get_syntask_image_name(
    syntask_version: Optional[str],
    python_version: Optional[str],
    flavor: Optional[str],
    expected: str,
):
    assert get_syntask_image_name(syntask_version, python_version, flavor) == expected
