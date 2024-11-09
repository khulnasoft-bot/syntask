"""
This initialization file makes the `BaseModel` and `SyntaskBaseModel` classes available for import from the pydantic module within Syntask. This setup allows other parts of the Syntask codebase to use these models without needing to understand the underlying compatibility layer.
"""
import typing
from syntask._internal.pydantic._flags import HAS_PYDANTIC_V2, USE_PYDANTIC_V2

if typing.TYPE_CHECKING:
    # import of virtually everything is supported via `__getattr__` below,
    # but we need them here for type checking and IDE support
    from pydantic import validator, root_validator
    from .main import (
        BaseModel,
        SyntaskBaseModel,
        FieldInfo,
        Field,
        PrivateAttr,
        SecretStr,
        field_validator,
        model_validator,
        ConfigDict,
        ValidationError,
    )

__all__ = [
    "BaseModel",
    "SyntaskBaseModel",
    "Field",
    "FieldInfo",
    "PrivateAttr",
    "SecretStr",
    "validator",
    "root_validator",
    "field_validator",
    "model_validator",
    "ConfigDict",
    "ValidationError",
]

_dynamic_imports: "typing.Dict[str, typing.Tuple[str, str]]" = {
    "BaseModel": ("syntask.pydantic", ".main"),
    "SyntaskBaseModel": ("syntask.pydantic", ".main"),
    "Field": ("syntask.pydantic", ".main"),
    "FieldInfo": ("syntask.pydantic", ".main"),
    "PrivateAttr": ("syntask.pydantic", ".main"),
    "SecretStr": ("syntask.pydantic", ".main"),
    "field_validator": ("syntask.pydantic", ".main"),
    "model_validator": ("syntask.pydantic", ".main"),
    "ConfigDict": ("syntask.pydantic", ".main"),
    "ValidationError": ("syntask.pydantic", ".main"),
}


def __getattr__(attr_name: str) -> object:
    from importlib import import_module

    if attr_name in _dynamic_imports:
        # If the attribute is in the dynamic imports, import it from the specified module
        package, module_name = _dynamic_imports[attr_name]

        # Prevent recursive import
        if module_name == "__module__":
            return import_module(f".{attr_name}", package=package)

        # Import the module and return the attribute
        else:
            module = import_module(module_name, package=package)
            return getattr(module, attr_name)

    elif HAS_PYDANTIC_V2 and not USE_PYDANTIC_V2:
        # In this case, we are using Pydantic v2 but it is not enabled, so we should import from pydantic.v1
        module = import_module("pydantic.v1")
        return getattr(module, attr_name)
    else:
        # In this case, we are using either Pydantic v1 or Pydantic v2 is enabled, so we should import from pydantic
        module = import_module("pydantic")
        return getattr(module, attr_name)
