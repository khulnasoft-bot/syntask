"""
Routes for interacting with block capabilities.
"""
from typing import List

from syntask._vendor.fastapi import Depends

from syntask.server import models
from syntask.server.database.dependencies import (
    SyntaskDBInterface,
    provide_database_interface,
)
from syntask.server.utilities.server import SyntaskRouter

router = SyntaskRouter(prefix="/block_capabilities", tags=["Block capabilities"])


@router.get("/")
async def read_available_block_capabilities(
    db: SyntaskDBInterface = Depends(provide_database_interface),
) -> List[str]:
    async with db.session_context() as session:
        return await models.block_schemas.read_available_block_capabilities(
            session=session
        )
