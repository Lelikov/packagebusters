from typing import Any, Protocol


class ISubGroupGetter(Protocol):
    def get_subgroup_ids(self, group_id: int) -> set: ...


class IProject(Protocol):
    id: int
    name: str
    web_url: str


class IProjectGetter(Protocol):
    def batch_get_projects(self, group_ids: set[int]) -> list[IProject]: ...


class IFile(Protocol):
    content: Any


class IFileGetter(Protocol):
    def batch_get_files(
        self, projects: list[IProject], file_path: str, is_cached: bool
    ) -> list[tuple[IProject, IFile | None]]: ...
