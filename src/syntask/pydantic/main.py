"""
This file defines a `SyntaskBaseModel` class that extends the `BaseModel` (imported from the internal compatibility layer).
"""
import typing

from syntask._internal.pydantic._compat import (
    BaseModel,
    ConfigDict,
    Field,
    FieldInfo,
    PrivateAttr,
    SecretStr,
    ValidationError,
    field_validator,
    model_validator,
)


class SyntaskBaseModel(BaseModel):
    def _reset_fields(self) -> typing.Set[str]:
        """
        A set of field names that are reset when the SyntaskBaseModel is copied.
        These fields are also disregarded for equality comparisons.
        """
        return set()


__all__ = [
    "BaseModel",
    "SyntaskBaseModel",
    "Field",
    "FieldInfo",
    "PrivateAttr",
    "SecretStr",
    "field_validator",
    "model_validator",
    "ConfigDict",
    "ValidationError",
]
