from typing import TypedDict


class Project(TypedDict):
    project_name: str
    project_url: str


class GroupPackage(TypedDict):
    package_name: str
    package_version: str
    projects: list[Project]
