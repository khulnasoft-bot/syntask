from typing import TYPE_CHECKING, Any, Sequence, Union

from typing_extensions import TypeAlias

if TYPE_CHECKING:
    from syntask.client.schemas.actions import DeploymentScheduleCreate
    from syntask.client.schemas.schedules import SCHEDULE_TYPES

FlexibleScheduleList: TypeAlias = Sequence[
    Union["DeploymentScheduleCreate", dict[str, Any], "SCHEDULE_TYPES"]
]
