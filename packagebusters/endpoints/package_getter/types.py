from pydantic import BaseModel


class Project(BaseModel):
    project_name: str
    project_url: str


class GroupPackage(BaseModel):
    package_name: str
    package_version: str
    projects: list[Project]
