from typing import Any, Protocol


class IGitLabClient(Protocol):
    groups: Any


class IGroupProject(Protocol):
    id: int
    name: str
    web_url: str
