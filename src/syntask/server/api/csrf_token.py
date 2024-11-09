from syntask._vendor.fastapi import Depends, Query, status
from syntask._vendor.starlette.exceptions import HTTPException

from syntask.logging import get_logger
from syntask.server import models, schemas
from syntask.server.database.dependencies import provide_database_interface
from syntask.server.database.interface import SyntaskDBInterface
from syntask.server.utilities.server import SyntaskRouter
from syntask.settings import SYNTASK_SERVER_CSRF_PROTECTION_ENABLED

logger = get_logger("server.api")

router = SyntaskRouter(prefix="/csrf-token")


@router.get("")
async def create_csrf_token(
    db: SyntaskDBInterface = Depends(provide_database_interface),
    client: str = Query(..., description="The client to create a CSRF token for"),
) -> schemas.core.CsrfToken:
    """Create or update a CSRF token for a client"""
    if SYNTASK_SERVER_CSRF_PROTECTION_ENABLED.value() is False:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="CSRF protection is disabled.",
        )

    async with db.session_context(begin_transaction=True) as session:
        token = await models.csrf_token.create_or_update_csrf_token(
            session=session, client=client
        )
        await models.csrf_token.delete_expired_tokens(session=session)

    return token
