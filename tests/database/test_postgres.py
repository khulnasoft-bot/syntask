import pytest
import sqlalchemy as sa

import syntask.settings
from syntask.settings import SYNTASK_API_DATABASE_CONNECTION_URL

pytestmark = pytest.mark.skipif(
    not SYNTASK_API_DATABASE_CONNECTION_URL.value_from(
        syntask.settings.get_settings_from_env()
    ).startswith("postgresql"),
    reason="These tests apply only to Postgres",
)


@pytest.fixture
async def populate(session, tests_dir):
    with open(tests_dir.joinpath("scripts", "populate_database.sql"), "r") as sql_file:
        raw_sql = sql_file.read().rstrip()
        stmts = raw_sql.split(";")

        async with session.begin():
            for stmt in stmts:
                if stmt:
                    await session.execute(sa.text(stmt))
