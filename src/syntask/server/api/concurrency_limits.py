"""
Routes for interacting with concurrency limit objects.
"""
from typing import List, Optional
from uuid import UUID

import pendulum
from syntask._vendor.fastapi import Body, Depends, HTTPException, Path, Response, status

import syntask.server.api.dependencies as dependencies
import syntask.server.models as models
import syntask.server.schemas as schemas
from syntask.server.database.dependencies import provide_database_interface
from syntask.server.database.interface import SyntaskDBInterface
from syntask.server.utilities.server import SyntaskRouter

router = SyntaskRouter(prefix="/concurrency_limits", tags=["Concurrency Limits"])


@router.post("/")
async def create_concurrency_limit(
    concurrency_limit: schemas.actions.ConcurrencyLimitCreate,
    response: Response,
    db: SyntaskDBInterface = Depends(provide_database_interface),
) -> schemas.core.ConcurrencyLimit:
    # hydrate the input model into a full model
    concurrency_limit_model = schemas.core.ConcurrencyLimit(**concurrency_limit.dict())

    async with db.session_context(begin_transaction=True) as session:
        model = await models.concurrency_limits.create_concurrency_limit(
            session=session, concurrency_limit=concurrency_limit_model
        )

    if model.created >= pendulum.now("UTC"):
        response.status_code = status.HTTP_201_CREATED

    return model


@router.get("/{id}")
async def read_concurrency_limit(
    concurrency_limit_id: UUID = Path(
        ..., description="The concurrency limit id", alias="id"
    ),
    db: SyntaskDBInterface = Depends(provide_database_interface),
) -> schemas.core.ConcurrencyLimit:
    """
    Get a concurrency limit by id.

    The `active slots` field contains a list of TaskRun IDs currently using a
    concurrency slot for the specified tag.
    """
    async with db.session_context() as session:
        model = await models.concurrency_limits.read_concurrency_limit(
            session=session, concurrency_limit_id=concurrency_limit_id
        )
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Concurrency limit not found"
        )
    return model


@router.get("/tag/{tag}")
async def read_concurrency_limit_by_tag(
    tag: str = Path(..., description="The tag name", alias="tag"),
    db: SyntaskDBInterface = Depends(provide_database_interface),
) -> schemas.core.ConcurrencyLimit:
    """
    Get a concurrency limit by tag.

    The `active slots` field contains a list of TaskRun IDs currently using a
    concurrency slot for the specified tag.
    """

    async with db.session_context() as session:
        model = await models.concurrency_limits.read_concurrency_limit_by_tag(
            session=session, tag=tag
        )

    if not model:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="Concurrency limit not found"
        )
    return model


@router.post("/filter")
async def read_concurrency_limits(
    limit: int = dependencies.LimitBody(),
    offset: int = Body(0, ge=0),
    db: SyntaskDBInterface = Depends(provide_database_interface),
) -> List[schemas.core.ConcurrencyLimit]:
    """
    Query for concurrency limits.

    For each concurrency limit the `active slots` field contains a list of TaskRun IDs
    currently using a concurrency slot for the specified tag.
    """
    async with db.session_context() as session:
        return await models.concurrency_limits.read_concurrency_limits(
            session=session,
            limit=limit,
            offset=offset,
        )


@router.post("/tag/{tag}/reset")
async def reset_concurrency_limit_by_tag(
    tag: str = Path(..., description="The tag name"),
    slot_override: Optional[List[UUID]] = Body(
        None,
        embed=True,
        description="Manual override for active concurrency limit slots.",
    ),
    db: SyntaskDBInterface = Depends(provide_database_interface),
):
    async with db.session_context(begin_transaction=True) as session:
        model = await models.concurrency_limits.reset_concurrency_limit_by_tag(
            session=session, tag=tag, slot_override=slot_override
        )
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Concurrency limit not found"
        )


@router.delete("/{id}")
async def delete_concurrency_limit(
    concurrency_limit_id: UUID = Path(
        ..., description="The concurrency limit id", alias="id"
    ),
    db: SyntaskDBInterface = Depends(provide_database_interface),
):
    async with db.session_context(begin_transaction=True) as session:
        result = await models.concurrency_limits.delete_concurrency_limit(
            session=session, concurrency_limit_id=concurrency_limit_id
        )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Concurrency limit not found"
        )


@router.delete("/tag/{tag}")
async def delete_concurrency_limit_by_tag(
    tag: str = Path(..., description="The tag name"),
    db: SyntaskDBInterface = Depends(provide_database_interface),
):
    async with db.session_context(begin_transaction=True) as session:
        result = await models.concurrency_limits.delete_concurrency_limit_by_tag(
            session=session, tag=tag
        )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Concurrency limit not found"
        )
