"""Schemas for _internal_ use within the Syntask server, but that would not be
appropriate for use on the API itself."""

from typing import Optional

from pydantic import Field

from syntask.server.schemas import actions, statuses


class InternalWorkPoolUpdate(actions.WorkPoolUpdate):
    status: Optional[statuses.WorkPoolStatus] = Field(default=None)
