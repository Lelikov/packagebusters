from typing import Protocol, TypedDict


class IProject(TypedDict):
    project_name: str
    project_url: str


class IGroupPackage(TypedDict):
    package_name: str
    package_version: str
    projects: list[IProject]


class IPackageGetter(Protocol):
    def get_group_packages(
        self,
        group_id: int,
        is_add_transitive_dependencies: bool,
        is_cached: bool,
    ) -> list[IGroupPackage]: ...
