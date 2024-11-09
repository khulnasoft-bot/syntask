import json
from typing import Dict, Type
from uuid import uuid4

import pendulum
import pytest

from syntask._internal.pydantic import HAS_PYDANTIC_V2
from syntask.settings import (
    SYNTASK_EVENTS_MAXIMUM_LABELS_PER_RESOURCE,
    SYNTASK_EVENTS_MAXIMUM_RELATED_RESOURCES,
    temporary_settings,
)

if HAS_PYDANTIC_V2:
    from pydantic.v1 import ValidationError
else:
    from pydantic import ValidationError


from syntask.server.events import (
    Event,
    LabelDiver,
    RelatedResource,
    Resource,
    ResourceSpecification,
)


def test_resource_openapi_schema() -> None:
    assert Resource.schema() == {
        "title": "Resource",
        "description": "An observable business object of interest to the user",
        "type": "object",
        "additionalProperties": {"type": "string"},
    }


def test_related_resource_openapi_schema() -> None:
    assert RelatedResource.schema() == {
        "title": "RelatedResource",
        "description": "A Resource with a specific role in an Event",
        "type": "object",
        "additionalProperties": {"type": "string"},
    }


@pytest.mark.parametrize(
    "resource_class", [Resource, RelatedResource, ResourceSpecification]
)
def test_resource_root_is_required(resource_class: Type[Resource]) -> None:
    with pytest.raises(ValidationError) as error:
        resource_class.parse_obj(None)

    assert error.value.errors() == [
        {
            "loc": ("__root__",),
            "msg": "none is not an allowed value",
            "type": "type_error.none.not_allowed",
        }
    ]


@pytest.mark.parametrize(
    "resource_class", [Resource, RelatedResource, ResourceSpecification]
)
def test_resource_root_is_a_dictionary(resource_class: Type[Resource]) -> None:
    with pytest.raises(ValidationError) as error:
        resource_class.parse_obj(11)

    assert error.value.errors() == [
        {
            "loc": ("__root__",),
            "msg": "value is not a valid dict",
            "type": "type_error.dict",
        }
    ]


@pytest.mark.parametrize("resource_class", [Resource, RelatedResource])
def test_resource_requires_resource_id(resource_class: Type[Resource]) -> None:
    with pytest.raises(ValidationError) as error:
        resource_class.parse_obj(
            {
                "syntask.resource.role": "any-role",
            }
        )

    assert error.value.errors() == [
        {
            "loc": ("__root__",),
            "msg": "Resources must include the syntask.resource.id label",
            "type": "value_error",
        }
    ]


def test_related_resources_require_role() -> None:
    with pytest.raises(ValidationError) as error:
        RelatedResource.parse_obj(
            {
                "syntask.resource.id": "my.unique.resource",
            }
        )

    assert error.value.errors() == [
        {
            "loc": ("__root__",),
            "msg": "Related Resources must include the syntask.resource.role label",
            "type": "value_error",
        },
    ]


def test_related_resources_require_non_empty_role() -> None:
    with pytest.raises(ValidationError) as error:
        RelatedResource.parse_obj(
            {
                "syntask.resource.id": "my.unique.resource",
                "syntask.resource.role": None,
            }
        )

    assert error.value.errors() == [
        {
            "loc": ("__root__",),
            "msg": "The syntask.resource.role label must be non-empty",
            "type": "value_error",
        },
    ]


@pytest.mark.parametrize("resource_class", [Resource, RelatedResource])
def test_resource_requires_non_empty_resource_id(
    resource_class: Type[Resource],
) -> None:
    with pytest.raises(ValidationError) as error:
        resource_class.parse_obj(
            {
                "syntask.resource.id": None,
                "syntask.resource.role": "any-role",
            }
        )

    assert error.value.errors() == [
        {
            "loc": ("__root__",),
            "msg": "The syntask.resource.id label must be non-empty",
            "type": "value_error",
        }
    ]


def test_empty_resource_specification_allowed_and_includes_all_resources() -> None:
    specification = ResourceSpecification.parse_obj({})
    assert specification.includes(
        [Resource.parse_obj({"syntask.resource.id": "any.thing", "any": "thing"})]
    )
    assert specification.includes(
        [
            Resource.parse_obj(
                {
                    "syntask.resource.id": "this.too",
                    "syntask.resource.role": "also",
                    "this": "too",
                }
            )
        ]
    )


@pytest.mark.parametrize("resource_class", [Resource, RelatedResource])
def test_resource_disallows_none_values(resource_class: Type[Resource]) -> None:
    with pytest.raises(ValidationError) as error:
        resource_class.parse_obj(
            {
                "syntask.resource.id": "my.unique.resource",
                "syntask.resource.role": "any-role",
                "another.thing": None,
            }
        )

    assert error.value.errors() == [
        {
            "loc": ("__root__", "another.thing"),
            "msg": "none is not an allowed value",
            "type": "type_error.none.not_allowed",
        },
    ]


@pytest.mark.parametrize("resource_class", [Resource, RelatedResource])
def test_resource_coerces_other_values(resource_class: Type[Resource]) -> None:
    resource = resource_class.parse_obj(
        {
            "syntask.resource.id": "my.unique.resource",
            "syntask.resource.role": "any-role",
            "another.thing": 5,
        }
    )
    assert resource["another.thing"] == "5"


@pytest.mark.parametrize("resource_class", [Resource, RelatedResource])
def test_resources_support_indexing(resource_class: Type[Resource]) -> None:
    resource = resource_class.parse_obj(
        {
            "syntask.resource.id": "my.unique.resource",
            "syntask.resource.role": "any-role",
            "this.thing": "hello",
            "that.thing": "world",
        }
    )
    assert resource["this.thing"] == "hello"
    assert resource["that.thing"] == "world"

    resource["this.thing"] = "goodbye"
    assert resource["this.thing"] == "goodbye"

    assert "new.thing" not in resource
    resource["new.thing"] = "new thing"
    assert resource["new.thing"] == "new thing"


@pytest.mark.parametrize("resource_class", [Resource, RelatedResource])
def test_resources_support_contains(resource_class: Type[Resource]) -> None:
    resource = resource_class.parse_obj(
        {
            "syntask.resource.id": "my.unique.resource",
            "syntask.resource.role": "any-role",
            "this.thing": "hello",
            "that.thing": "world",
        }
    )
    assert "this.thing" in resource
    assert "that.thing" in resource


@pytest.mark.parametrize("resource_class", [Resource, RelatedResource])
def test_resource_id_shortcut(resource_class: Type[Resource]) -> None:
    resource = resource_class.parse_obj(
        {
            "syntask.resource.id": "my.unique.resource",
            "syntask.resource.role": "any-role",
        }
    )
    assert resource.id == "my.unique.resource"


def test_resource_role_shortcut() -> None:
    resource = RelatedResource.parse_obj(
        {
            "syntask.resource.id": "my.unique.resource",
            "syntask.resource.role": "any-role",
        }
    )
    assert resource.role == "any-role"


@pytest.mark.parametrize("resource_class", [Resource, RelatedResource])
def test_resource_labels_are_iterable(resource_class: Type[Resource]) -> None:
    resource = resource_class.parse_obj(
        {
            "syntask.resource.id": "my.unique.resource",
            "syntask.resource.role": "any-role",
            "hello": "world",
            "goodbye": "moon",
        }
    )
    assert set(resource.keys()) == {
        "syntask.resource.id",
        "syntask.resource.role",
        "hello",
        "goodbye",
    }


@pytest.mark.parametrize("resource_class", [Resource, RelatedResource])
def test_resource_label_pairs_are_iterable(resource_class: Type[Resource]) -> None:
    resource = resource_class.parse_obj(
        {
            "syntask.resource.id": "my.unique.resource",
            "syntask.resource.role": "any-role",
            "hello": "world",
            "goodbye": "moon",
        }
    )
    assert set(resource.items()) == {
        ("syntask.resource.id", "my.unique.resource"),
        ("syntask.resource.role", "any-role"),
        ("hello", "world"),
        ("goodbye", "moon"),
    }


@pytest.mark.parametrize("resource_class", [Resource, RelatedResource])
def test_resources_export_to_simple_dicts(resource_class: Type[Resource]) -> None:
    resource = resource_class.parse_obj(
        {
            "syntask.resource.id": "my.unique.resource",
            "syntask.resource.role": "any-role",
            "hello": "world",
            "goodbye": "moon",
        }
    )
    assert json.loads(resource.json()) == {
        "syntask.resource.id": "my.unique.resource",
        "syntask.resource.role": "any-role",
        "hello": "world",
        "goodbye": "moon",
    }


@pytest.mark.parametrize("resource_class", [Resource, RelatedResource])
def test_resources_export_label_value_arrays(resource_class: Type[Resource]) -> None:
    resource = resource_class.parse_obj(
        {
            "syntask.resource.id": "my.unique.resource",
            "syntask.resource.role": "any-role",
            "hello": "world",
            "goodbye": "moon",
        }
    )
    assert resource.as_label_value_array() == [
        {"label": "syntask.resource.id", "value": "my.unique.resource"},
        {"label": "syntask.resource.role", "value": "any-role"},
        {"label": "hello", "value": "world"},
        {"label": "goodbye", "value": "moon"},
    ]


@pytest.mark.parametrize("resource_class", [Resource, RelatedResource])
def test_resources_can_test_for_labels(resource_class: Type[Resource]) -> None:
    resource = resource_class.parse_obj(
        {
            "syntask.resource.id": "my.unique.resource",
            "syntask.resource.role": "any-role",
            "hello": "world",
            "goodbye": "moon",
        }
    )
    assert resource.has_all_labels({"hello": "world"})
    assert resource.has_all_labels({"hello": "world", "goodbye": "moon"})
    assert not resource.has_all_labels({"hello": "world", "goodbye": "mars"})


@pytest.mark.parametrize("resource_class", [Resource, RelatedResource])
def test_resources_provide_label_divers(resource_class: Type[Resource]) -> None:
    resource = resource_class.parse_obj(
        {
            "syntask.resource.id": "my.unique.resource",
            "syntask.resource.role": "any-role",
            "hello": "world",
            "goodbye": "moon",
        }
    )
    assert isinstance(resource.labels, LabelDiver)
    assert str(resource.labels.hello) == "world"


def test_label_diving_repr():
    representation = repr(
        LabelDiver(
            {
                "first": "a",
                "first.second": "b",
                "first.second.third": "c",
                "first.second.fourth": "d",
                "fifth.sixth": "e",
                "seventh": "f",
            }
        )
    )
    assert representation.startswith("LabelDiver(")
    assert "first" in representation
    assert "first.second" not in representation
    assert representation.endswith(")")


def test_label_diving():
    diver = LabelDiver(
        {
            "first": "a",
            "first.second": "b",
            "first.second.third": "c",
            "first.second.fourth": "d",
            "fifth.sixth": "e",
            "seventh": "f",
        }
    )

    assert str(diver.first) == "a"
    assert str(diver.first.second) == "b"
    assert str(diver.first.second.third) == "c"
    assert str(diver.first.second.fourth) == "d"
    assert str(diver.fifth.sixth) == "e"

    assert diver["first"] == "a"
    assert diver["first.second"] == "b"

    assert len(diver) == 6
    assert set(diver) == {
        ("first", "a"),
        ("first.second", "b"),
        ("first.second.third", "c"),
        ("first.second.fourth", "d"),
        ("fifth.sixth", "e"),
        ("seventh", "f"),
    }

    with pytest.raises(AttributeError):
        diver.non_existant

    with pytest.raises(AttributeError):
        diver.first.non_existant

    with pytest.raises(AttributeError):
        diver.seventh.eighth

    with pytest.raises(AttributeError):
        diver._something_else

    with pytest.raises(AttributeError):
        getattr(diver, "_something_else")


def test_limit_on_labels():
    with temporary_settings(updates={SYNTASK_EVENTS_MAXIMUM_LABELS_PER_RESOURCE: 10}):
        with pytest.raises(ValidationError, match="maximum number of labels"):
            Resource.parse_obj(
                {
                    "syntask.resource.id": "the.thing",
                    **{str(i): str(i) for i in range(10)},
                }
            )


def test_limit_on_related_resources():
    with temporary_settings(updates={SYNTASK_EVENTS_MAXIMUM_RELATED_RESOURCES: 10}):
        with pytest.raises(ValidationError, match="maximum number of related"):
            Event(
                occurred=pendulum.now("UTC"),
                event="anything",
                resource={"syntask.resource.id": "the.thing"},
                related=[
                    {
                        "syntask.resource.id": f"another.thing.{i}",
                        "syntask.resource.role": "related",
                    }
                    for i in range(11)
                ],
                id=uuid4(),
            )


@pytest.mark.parametrize("resource_class", [Resource, RelatedResource])
@pytest.mark.parametrize(
    "example",
    [
        {"a-label": "a-value"},
        {"a-label": "a-value", "another-label": "a-value"},
        {"a-label": "a-value", "another-label": "another-value"},
    ],
)
def test_resource_specification_matches_resource(
    resource_class: Type[Resource], example: Dict[str, str]
):
    specification = ResourceSpecification.parse_obj({"a-label": "a-value"})

    resource = resource_class.parse_obj(
        {
            "syntask.resource.id": "anything",
            "syntask.resource.role": "anyhoo",
            **example,
        }
    )

    assert specification.matches(resource)
    assert specification.includes([resource])


@pytest.mark.parametrize("resource_class", [Resource, RelatedResource])
@pytest.mark.parametrize(
    "example",
    [
        {"a-label": "a-value"},
        {"a-label": "a-value", "another-label": "a-value"},
        {"a-label": "a-value", "another-label": "another-value"},
        {"a-label": "a-val", "another-label": "another-value"},
        {"a-label": "a-valerie", "another-label": "another-value"},
        {"a-label": "a-val kilmer", "another-label": "another-value"},
        {"a-label": "a-valiant-effort", "another-label": "another-value"},
        {"a-label": "a-val.iant-effort", "another-label": "another-value"},
    ],
)
def test_resource_specification_wildcard_matches_resource(
    resource_class: Type[Resource], example: Dict[str, str]
):
    specification = ResourceSpecification.parse_obj({"a-label": "a-val*"})

    resource = resource_class.parse_obj(
        {
            "syntask.resource.id": "anything",
            "syntask.resource.role": "anyhoo",
            **example,
        }
    )

    assert specification.matches(resource)
    assert specification.includes([resource])


@pytest.mark.parametrize("resource_class", [Resource, RelatedResource])
@pytest.mark.parametrize(
    "example",
    [
        {},
        {"a-label": "another-value"},
        {"a-label": ""},
        {"another-label": "another-value"},
    ],
)
def test_resource_specification_does_not_match_resource(
    resource_class: Type[Resource], example: Dict[str, str]
):
    specification = ResourceSpecification.parse_obj({"a-label": "a-value"})

    resource = resource_class.parse_obj(
        {
            "syntask.resource.id": "anything",
            "syntask.resource.role": "anyhoo",
            **example,
        }
    )

    assert not specification.matches(resource)
    assert not specification.includes([resource])


@pytest.mark.parametrize("resource_class", [Resource, RelatedResource])
@pytest.mark.parametrize(
    "example",
    [
        {},
        {"a-label": "another-value"},
        {"a-label": ""},
        {"another-label": "another-value"},
        {"a-label": "a-vanquishment"},
        {"a-label": "a-va"},
    ],
)
def test_resource_specification_wildcard_does_not_match_resource(
    resource_class: Type[Resource], example: Dict[str, str]
):
    specification = ResourceSpecification.parse_obj({"a-label": "a-val*"})

    resource = resource_class.parse_obj(
        {
            "syntask.resource.id": "anything",
            "syntask.resource.role": "anyhoo",
            **example,
        }
    )

    assert not specification.matches(resource)
    assert not specification.includes([resource])


@pytest.mark.parametrize("resource_class", [Resource, RelatedResource])
def test_resource_specification_matches_every_resource(resource_class: Type[Resource]):
    specification = ResourceSpecification.parse_obj({})
    assert specification.matches_every_resource()
    assert specification.matches_every_resource_of_kind("anything")
    assert specification.matches_every_resource_of_kind("yep.this.too")

    resource = resource_class.parse_obj(
        {
            "syntask.resource.id": "anything",
            "syntask.resource.role": "anyhoo",
        }
    )
    assert specification.matches(resource)
    assert specification.includes([resource])


@pytest.mark.parametrize("resource_class", [Resource, RelatedResource])
def test_resource_specification_matches_every_resource_of_kind(
    resource_class: Type[Resource],
):
    specification = ResourceSpecification.parse_obj(
        {"syntask.resource.id": "any.old.*"}
    )
    assert not specification.matches_every_resource()
    assert specification.matches_every_resource_of_kind("any.old")
    assert not specification.matches_every_resource_of_kind("nope.not.this")

    resource = resource_class.parse_obj(
        {
            "syntask.resource.id": "any.old.thing",
            "syntask.resource.role": "anyhoo",
        }
    )
    assert specification.matches(resource)
    assert specification.includes([resource])


def test_resource_specification_does_not_match_every_resource_of_kind():
    specification = ResourceSpecification.parse_obj(
        {"syntask.resource.id": "any.old.*", "but-also": "another-thing"}
    )
    assert not specification.matches_every_resource()
    assert not specification.matches_every_resource_of_kind("any.old")

    specification = ResourceSpecification.parse_obj({"but-also": "another-thing"})
    assert not specification.matches_every_resource()
    assert not specification.matches_every_resource_of_kind("any.old")


def test_resource_specification_is_dictlike():
    specification = ResourceSpecification.parse_obj(
        {
            "syntask.resource.id": "any.old.*",
            "but-also": ["another-thing", "or-this"],
            "": ["is kinda weird"],
            "also": "kinda weird",
            "empty": "",
        }
    )

    assert specification["syntask.resource.id"] == ["any.old.*"]
    assert specification["but-also"] == ["another-thing", "or-this"]
    assert specification[""] == ["is kinda weird"]
    assert specification["also"] == ["kinda weird"]
    assert specification["empty"] == []
    with pytest.raises(KeyError):
        assert specification["not-here"]

    assert specification.get("syntask.resource.id") == ["any.old.*"]
    assert specification.get("but-also") == ["another-thing", "or-this"]
    assert specification.get("") == ["is kinda weird"]
    assert specification.get("also") == ["kinda weird"]
    assert specification.get("empty") == []
    assert specification.get("not-here") == []
    assert specification.get("not-here", "foo") == ["foo"]

    assert "syntask.resource.id" in specification
    assert specification.pop("syntask.resource.id") == ["any.old.*"]
    assert "syntask.resource.id" not in specification

    assert "but-also" in specification
    assert specification.pop("but-also") == ["another-thing", "or-this"]
    assert "but-also" not in specification

    assert "whatever" not in specification
    assert specification.pop("whatever", None) == []
    assert specification.pop("whatever", "foo") == ["foo"]
    assert "whatever" not in specification


def test_resource_specification_deepcopy():
    specification = ResourceSpecification.parse_obj(
        {
            "syntask.resource.id": "any.old.*",
            "but-also": ["another-thing", "or-this"],
        }
    )
    copy = specification.deepcopy()
    assert specification == copy
    assert specification is not copy
    assert specification["syntask.resource.id"] == copy["syntask.resource.id"]
    assert specification["but-also"] == copy["but-also"]
    assert specification["but-also"] is not copy["but-also"]
