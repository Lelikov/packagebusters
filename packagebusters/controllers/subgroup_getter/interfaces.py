from typing import Any, Protocol


class IGitLabClient(Protocol):
    groups: Any


class IGroupDescendantGroup(Protocol):
    id: int
