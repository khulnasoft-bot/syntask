import datetime
import importlib
import os
from contextlib import contextmanager
from typing import Generator, Type
from uuid import UUID, uuid4

import pendulum

from syntask._internal.pydantic import HAS_PYDANTIC_V2

if HAS_PYDANTIC_V2:
    import pydantic.v1 as pydantic
else:
    import pydantic

import pytest

from syntask.server.utilities.schemas import (
    DateTimeTZ,
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
            pydantic.ValidationError, match="extra fields not permitted"
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
            pydantic.ValidationError, match="extra fields not permitted"
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
        assert nested.dict() == {"x": 1, "y": {"z": 2}}
        assert isinstance(nested.dict()["y"], dict)

    def test_simple_dict(self, nested):
        assert dict(nested) == {"x": 1, "y": nested.y}
        assert isinstance(dict(nested)["y"], pydantic.BaseModel)

    def test_shallow_true(self, nested):
        assert dict(nested) == nested.dict(shallow=True)
        assert isinstance(nested.dict(shallow=True)["y"], pydantic.BaseModel)

    def test_kwargs_respected(self, nested):
        deep = nested.dict(include={"y"})
        shallow = nested.dict(include={"y"}, shallow=True)
        assert isinstance(deep["y"], dict)
        assert isinstance(shallow["y"], pydantic.BaseModel)
        assert deep == shallow == {"y": {"z": 2}}


class TestJsonCompatibleDict:
    class Model(SyntaskBaseModel):
        x: UUID
        y: datetime.datetime

    @pytest.fixture()
    def nested(self):
        class Child(pydantic.BaseModel):
            z: UUID

        class Parent(SyntaskBaseModel):
            x: UUID
            y: Child

        return Parent(x=uuid4(), y=Child(z=uuid4()))

    def test_json_compatible_and_nested_errors(self):
        model = self.Model(x=uuid4(), y=pendulum.now("UTC"))
        with pytest.raises(ValueError, match="(only be applied to the entire object)"):
            model.dict(json_compatible=True, shallow=True)

    def test_json_compatible(self):
        model = self.Model(x=uuid4(), y=pendulum.now("UTC"))
        d1 = model.dict()
        d2 = model.dict(json_compatible=True)

        assert isinstance(d1["x"], UUID) and d1["x"] == model.x
        assert isinstance(d2["x"], str) and d2["x"] == str(model.x)

        assert isinstance(d1["y"], datetime.datetime) and d1["y"] == model.y
        assert isinstance(d2["y"], str) and d2["y"] == model.y.isoformat()

    def test_json_applies_to_nested(self, nested):
        d1 = nested.dict(json_compatible=True)
        assert isinstance(d1["x"], str) and d1["x"] == str(nested.x)
        assert isinstance(d1["y"]["z"], str) and d1["y"]["z"] == str(nested.y.z)


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


class TestDatetimeTZ:
    class Model(pydantic.BaseModel):
        dt: datetime.datetime
        dtp: pendulum.DateTime
        dttz: DateTimeTZ

    async def test_tz_adds_timezone(self):
        model = self.Model(
            dt=datetime.datetime(2022, 1, 1),
            dtp=datetime.datetime(2022, 1, 1),
            dttz=datetime.datetime(2022, 1, 1),
        )

        assert model.dt.tzinfo is None
        assert model.dtp.tzinfo is None
        assert model.dttz.tzinfo.name == "UTC"

    async def test_tz_is_pydantic_object(self):
        model = self.Model(
            dt=datetime.datetime(2022, 1, 1),
            dtp=datetime.datetime(2022, 1, 1),
            dttz=datetime.datetime(2022, 1, 1),
        )
        assert not isinstance(model.dt, pendulum.DateTime)
        # typing as pendulum datetime doesn't result in pendulum datetime
        assert not isinstance(model.dtp, pendulum.DateTime)
        assert isinstance(model.dttz, pendulum.DateTime)
