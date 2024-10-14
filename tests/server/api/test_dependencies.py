from typing import Optional

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from syntask.server.api.dependencies import get_syntask_client_version


@pytest.mark.parametrize(
    "header,expected",
    [
        ("syntask/2.19.6 (API 0.8.4)", "2.19.6"),
        ("syntask/3.0.1 (API 2.19.3)", "3.0.1"),
        ("syntask/3.0.3+20.g6a5cc73fb6 (API 0.8.4)", "3.0.3+20.g6a5cc73fb6"),
        ("syntask/3.0.3rc3 (API unknown)", "3.0.3rc3"),
        (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            None,
        ),
        ("random", None),
        ("", None),
        (None, None),
    ],
)
def test_get_syntask_client_version_correctly_extracts_from_header(
    header: str, expected: str
):
    app = FastAPI()

    @app.get("/version")
    async def get_version(
        syntask_client_version: Optional[str] = Depends(get_syntask_client_version),
    ):
        return syntask_client_version

    with TestClient(app) as client:
        response = client.get(
            "/version", headers={"User-Agent": header} if header is not None else {}
        )
        assert response.status_code == 200
        assert response.json() == expected
