"""
Routes for admin-level interactions with the Syntask REST API.
"""
from syntask._vendor.fastapi import Body, Depends, Response, status

import syntask
import syntask.settings
from syntask.server.database.dependencies import provide_database_interface
from syntask.server.database.interface import SyntaskDBInterface
from syntask.server.utilities.server import SyntaskRouter

router = SyntaskRouter(prefix="/admin", tags=["Admin"])


@router.get("/settings")
async def read_settings() -> syntask.settings.Settings:
    """
    Get the current Syntask REST API settings.

    Secret setting values will be obfuscated.
    """
    return syntask.settings.get_current_settings().with_obfuscated_secrets()


@router.get("/version")
async def read_version() -> str:
    """Returns the Syntask version number"""
    return syntask.__version__


@router.post("/database/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_database(
    db: SyntaskDBInterface = Depends(provide_database_interface),
    confirm: bool = Body(
        False,
        embed=True,
        description="Pass confirm=True to confirm you want to modify the database.",
    ),
    response: Response = None,
):
    """Clear all database tables without dropping them."""
    if not confirm:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return
    async with db.session_context(begin_transaction=True) as session:
        # work pool has a circular dependency on pool queue; delete it first
        await session.execute(db.WorkPool.__table__.delete())
        for table in reversed(db.Base.metadata.sorted_tables):
            await session.execute(table.delete())


@router.post("/database/drop", status_code=status.HTTP_204_NO_CONTENT)
async def drop_database(
    db: SyntaskDBInterface = Depends(provide_database_interface),
    confirm: bool = Body(
        False,
        embed=True,
        description="Pass confirm=True to confirm you want to modify the database.",
    ),
    response: Response = None,
):
    """Drop all database objects."""
    if not confirm:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return

    await db.drop_db()


@router.post("/database/create", status_code=status.HTTP_204_NO_CONTENT)
async def create_database(
    db: SyntaskDBInterface = Depends(provide_database_interface),
    confirm: bool = Body(
        False,
        embed=True,
        description="Pass confirm=True to confirm you want to modify the database.",
    ),
    response: Response = None,
):
    """Create all database objects."""
    if not confirm:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return

    await db.create_db()
