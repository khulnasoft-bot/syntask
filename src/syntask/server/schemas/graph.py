from datetime import datetime
from typing import Any, List, Literal, Optional, Tuple
from uuid import UUID

from syntask.server.schemas.states import StateType
from syntask.server.utilities.schemas import SyntaskBaseModel


class GraphState(SyntaskBaseModel):
    id: UUID
    timestamp: datetime
    type: StateType
    name: str


class GraphArtifact(SyntaskBaseModel):
    id: UUID
    created: datetime
    key: Optional[str]
    type: str
    is_latest: bool
    data: Optional[Any]  # we only return data for progress artifacts for now


class Edge(SyntaskBaseModel):
    id: UUID


class Node(SyntaskBaseModel):
    kind: Literal["flow-run", "task-run"]
    id: UUID
    label: str
    state_type: StateType
    start_time: datetime
    end_time: Optional[datetime]
    parents: List[Edge]
    children: List[Edge]
    encapsulating: List[Edge]
    artifacts: List[GraphArtifact]


class Graph(SyntaskBaseModel):
    start_time: datetime
    end_time: Optional[datetime]
    root_node_ids: List[UUID]
    nodes: List[Tuple[UUID, Node]]
    artifacts: List[GraphArtifact]
    states: List[GraphState]
