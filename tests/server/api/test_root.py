from starlette import status

from syntask.testing.utilities import AsyncMock


async def test_hello_world(client):
    response = await client.get("/hello")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == "👋"


async def test_ready(client):
    response = await client.get("/ready")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "OK"}


async def test_ready_with_unavailable_db(client, monkeypatch):
    is_db_connectable_mock = AsyncMock(return_value=False)

    monkeypatch.setattr(
        "syntask.server.database.interface.SyntaskDBInterface.is_db_connectable",
        is_db_connectable_mock,
    )
    response = await client.get("/ready")
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json() == {"message": "Database is not available"}
