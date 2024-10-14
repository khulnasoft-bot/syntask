import importlib
import os
from contextlib import contextmanager
from typing import Generator, Type
from uuid import uuid4

import pendulum
import pydantic
import pytest

from syntask.server.utilities.schemas import (
    IDBaseModel,
    ORMBaseModel,
    SyntaskBaseModel,
)


@contextmanager
def reload_syntask_base_model(
    test_mode_value,
) -> Generator[Type[SyntaskBaseModel], None, None]:
    import syntask.server.utilities.schemas.bases

    original_base_model = syntask.server.utilities.schemas.bases.SyntaskBaseModel
    original_environment = os.environ.get("SYNTASK_TEST_MODE")
    if test_mode_value is not None:
        os.environ["SYNTASK_TEST_MODE"] = test_mode_value
    else:
        os.environ.pop("SYNTASK_TEST_MODE")

    try:
        # We must re-execute the module since the setting is configured at base model
        # definition time
        importlib.reload(syntask.server.utilities.schemas.bases)

        from syntask.server.utilities.schemas.bases import SyntaskBaseModel

        yield SyntaskBaseModel
    finally:
        if original_environment is None:
            os.environ.pop("SYNTASK_TEST_MODE")
        else:
            os.environ["SYNTASK_TEST_MODE"] = original_environment

        # We must restore this type or `isinstance` checks will fail later
        syntask.server.utilities.schemas.bases.SyntaskBaseModel = original_base_model


class TestExtraForbidden:
    def test_extra_attributes_are_forbidden_during_unit_tests(self):
        class Model(SyntaskBaseModel):
            x: int

        with pytest.raises(
            pydantic.ValidationError, match="Extra inputs are not permitted"
        ):
            Model(x=1, y=2)

    @pytest.mark.parametrize("falsey_value", ["0", "False", "", None])
    def test_extra_attributes_are_allowed_outside_test_mode(self, falsey_value):
        with reload_syntask_base_model(falsey_value) as SyntaskBaseModel:

            class Model(SyntaskBaseModel):
                x: int

        Model(x=1, y=2)

    @pytest.mark.parametrize("truthy_value", ["1", "True", "true"])
    def test_extra_attributes_are_not_allowed_with_truthy_test_mode(self, truthy_value):
        with reload_syntask_base_model(truthy_value) as SyntaskBaseModel:

            class Model(SyntaskBaseModel):
                x: int

        with pytest.raises(
            pydantic.ValidationError, match="Extra inputs are not permitted"
        ):
            Model(x=1, y=2)


class TestNestedDict:
    @pytest.fixture()
    def nested(self):
        class Child(pydantic.BaseModel):
            z: int

        class Parent(SyntaskBaseModel):
            x: int
            y: Child

        return Parent(x=1, y=Child(z=2))

    def test_full_dict(self, nested):
        assert nested.model_dump() == {"x": 1, "y": {"z": 2}}
        assert isinstance(nested.model_dump()["y"], dict)

    def test_simple_dict(self, nested):
        assert dict(nested) == {"x": 1, "y": nested.y}
        assert isinstance(dict(nested)["y"], pydantic.BaseModel)

    def test_custom_dump_methods_respected(self, nested: SyntaskBaseModel):
        deep = nested.model_dump(include={"y"})
        shallow = nested.model_dump_for_orm(include={"y"})
        assert isinstance(deep["y"], dict)
        assert isinstance(shallow["y"], pydantic.BaseModel)


class CopyOnValidationChild(ORMBaseModel):
    x: int


class CopyOnValidationParent(ORMBaseModel):
    x: int
    child: CopyOnValidationChild


def test_assignment_preserves_ids():
    child_id = uuid4()
    parent_id = uuid4()
    child = CopyOnValidationChild(id=child_id, x=1)
    parent = CopyOnValidationParent(id=parent_id, x=1, child=child)
    assert child.id == child_id
    assert parent.id == parent_id
    # without the copy_on_model_validation = False flag
    # this test would fail
    assert parent.child.id == child_id


class TestEqualityExcludedFields:
    def test_idbasemodel_equality(self):
        class X(IDBaseModel):
            x: int

        assert X(id=uuid4(), x=1) == X(id=uuid4(), x=1)
        assert X(id=uuid4(), x=1) != X(id=uuid4(), x=2)

    def test_ormbasemodel_equality(self):
        class X(ORMBaseModel):
            x: int

        x1 = X(id=uuid4(), created=pendulum.now("UTC"), x=1)
        x2 = X(id=uuid4(), created=pendulum.now("UTC").add(hours=1), x=1)
        x3 = X(id=uuid4(), created=pendulum.now("UTC").subtract(hours=1), x=2)
        assert x1 == x2
        assert x1.created != x2.created
        assert x1 != x3

    def test_mixed_model_equality(self):
        class X(IDBaseModel):
            val: int

        class Y(ORMBaseModel):
            val: int

        class Z(SyntaskBaseModel):
            val: int

        class A(pydantic.BaseModel):
            val: int

        x = X(val=1)
        y = Y(val=1)
        z = Z(val=1)
        a = A(val=1)

        assert x == y == z == a
        assert x.id != y.id

    def test_right_equality_fails(self):
        class X(IDBaseModel):
            val: int

        class Y(pydantic.BaseModel):
            val: int

        assert X(val=1) == Y(val=1)
        # if the PBM is the RH operand, the equality check fails
        # because the Pydantic logic of using every field is applied
        assert Y(val=1) != X(val=1)
