from typing import Any, Protocol


class IGitLabClient(Protocol):
    projects: Any


class IProjectFile(Protocol):
    content: Any


class IProject(Protocol):
    id: int
    name: str
    web_url: str


class IFileCache(Protocol):
    def get(self, project_id: int, file_path: str) -> Any: ...

    def set(self, project_id: int, file_path: str, content: Any) -> None: ...
