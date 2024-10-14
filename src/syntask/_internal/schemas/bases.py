"""
Utilities for creating and working with Syntask REST API schemas.
"""

import datetime
import os
from typing import Any, ClassVar, Optional, Set, TypeVar
from uuid import UUID, uuid4

import pendulum
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)
from pydantic_extra_types.pendulum_dt import DateTime
from typing_extensions import Self

T = TypeVar("T")


class SyntaskBaseModel(BaseModel):
    """A base pydantic.BaseModel for all Syntask schemas and pydantic models.

    As the basis for most Syntask schemas, this base model usually ignores extra
    fields that are passed to it at instantiation. Because adding new fields to
    API payloads is not considered a breaking change, this ensures that any
    Syntask client loading data from a server running a possibly-newer version
    of Syntask will be able to process those new fields gracefully. However,
    when SYNTASK_TEST_MODE is on, extra fields are forbidden in order to catch
    subtle unintentional testing errors.
    """

    _reset_fields: ClassVar[Set[str]] = set()

    model_config = ConfigDict(
        ser_json_timedelta="float",
        defer_build=True,
        extra=(
            "ignore"
            if os.getenv("SYNTASK_TEST_MODE", "0").lower() not in ["true", "1"]
            else "forbid"
        ),
    )

    def __eq__(self, other: Any) -> bool:
        """Equaltiy operator that ignores the resettable fields of the SyntaskBaseModel.

        NOTE: this equality operator will only be applied if the SyntaskBaseModel is
        the left-hand operand. This is a limitation of Python.
        """
        copy_dict = self.model_dump(exclude=self._reset_fields)
        if isinstance(other, SyntaskBaseModel):
            return copy_dict == other.model_dump(exclude=other._reset_fields)
        if isinstance(other, BaseModel):
            return copy_dict == other.model_dump()
        else:
            return copy_dict == other

    def __rich_repr__(self):
        # Display all of the fields in the model if they differ from the default value
        for name, field in self.model_fields.items():
            value = getattr(self, name)

            # Simplify the display of some common fields
            if field.annotation == UUID and value:
                value = str(value)
            elif (
                isinstance(field.annotation, datetime.datetime)
                and name == "timestamp"
                and value
            ):
                value = pendulum.instance(value).isoformat()
            elif isinstance(field.annotation, datetime.datetime) and value:
                value = pendulum.instance(value).diff_for_humans()

            yield name, value, field.get_default()

    def reset_fields(self: Self) -> Self:
        """
        Reset the fields of the model that are in the `_reset_fields` set.

        Returns:
            SyntaskBaseModel: A new instance of the model with the reset fields.
        """
        return self.model_copy(
            update={
                field: self.model_fields[field].get_default(call_default_factory=True)
                for field in self._reset_fields
            }
        )


class IDBaseModel(SyntaskBaseModel):
    """
    A SyntaskBaseModel with an auto-generated UUID ID value.

    The ID is reset on copy() and not included in equality comparisons.
    """

    _reset_fields: ClassVar[Set[str]] = {"id"}
    id: UUID = Field(default_factory=uuid4)


class ObjectBaseModel(IDBaseModel):
    """
    A SyntaskBaseModel with an auto-generated UUID ID value and created /
    updated timestamps, intended for compatibility with our standard ORM models.

    The ID, created, and updated fields are reset on copy() and not included in
    equality comparisons.
    """

    _reset_fields: ClassVar[Set[str]] = {"id", "created", "updated"}
    model_config = ConfigDict(from_attributes=True)

    created: Optional[DateTime] = Field(default=None, repr=False)
    updated: Optional[DateTime] = Field(default=None, repr=False)


class ActionBaseModel(SyntaskBaseModel):
    model_config: ConfigDict = ConfigDict(extra="forbid")
