import base64
import re
import tomllib
from collections import defaultdict
from collections.abc import Generator
from contextlib import suppress
from itertools import chain
from typing import Any, Final

from packaging.version import parse as parse_version

from .interface import (
    IFileGetter,
    IProject,
    IProjectGetter,
    ISubGroupGetter,
)
from .types import GroupPackage


VERSION_UNKNOWN: Final[str] = "Version Unknown"


class PackageGetter:
    def __init__(
        self,
        subgroup_getter: ISubGroupGetter,
        project_getter: IProjectGetter,
        file_getter: IFileGetter,
    ) -> None:
        self.subgroup_getter: ISubGroupGetter = subgroup_getter
        self.project_getter: IProjectGetter = project_getter
        self.file_getter: IFileGetter = file_getter

    def get_group_packages(
        self, group_id: int, is_add_transitive_dependencies: bool, is_cached: bool
    ) -> Generator[GroupPackage, Any, None]:
        subgroup_ids: set[int] = self.subgroup_getter.get_subgroup_ids(group_id=group_id)
        projects: list[IProject] = self.project_getter.batch_get_projects(group_ids={*subgroup_ids, group_id})
        files = self._get_files(
            projects=projects,
            is_add_transitive_dependencies=is_add_transitive_dependencies,
            is_cached=is_cached,
        )
        group_packages: defaultdict = self._add_project_to_packages(
            files=files,
            is_add_transitive_dependencies=is_add_transitive_dependencies,
        )

        return self._get_sorted_group_packages(group_packages)

    def _get_files(
        self, projects: list[IProject], is_add_transitive_dependencies: bool, is_cached: bool
    ) -> dict[IProject, dict[str, str | None]]:
        poetry_lock_files = self.file_getter.batch_get_files(
            projects=projects,
            file_path="poetry.lock",
            is_cached=is_cached,
        )
        projects_with_poetry: list[IProject] = [project for project, file in poetry_lock_files if file]
        dockerfiles = self.file_getter.batch_get_files(
            projects=projects_with_poetry,
            file_path="Dockerfile",
            is_cached=is_cached,
        )

        files: dict[IProject, dict[str, Any]] = {
            project: {"poetry.lock": file.content} for project, file in poetry_lock_files if file
        }

        for project, file in dockerfiles:
            files[project].update({"Dockerfile": file.content if file else None})

        if not is_add_transitive_dependencies:
            pyproject_toml_files = self.file_getter.batch_get_files(
                projects=projects_with_poetry,
                file_path="pyproject.toml",
                is_cached=is_cached,
            )
            for project, file in pyproject_toml_files:
                files[project].update({"pyproject.toml": file.content if file else None})

        return files

    def _add_project_to_packages(
        self,
        files: dict[IProject, dict[str, str | None]],
        is_add_transitive_dependencies: bool,
    ) -> defaultdict:
        group_packages: defaultdict = defaultdict(lambda: defaultdict(list))

        for project, project_files in files.items():
            poetry_lock_packages: dict = self._get_poetry_lock_packages(file=project_files["poetry.lock"])
            dependencies: set = (
                set(poetry_lock_packages.keys())
                if is_add_transitive_dependencies
                else self._get_pyproject_toml_packages(file=project_files["pyproject.toml"])
            )

            if dockerfile := project_files.get("Dockerfile"):
                python_version: str = self._get_python_version(dockerfile)
                self._add_dependence_to_group_packages(
                    group_packages=group_packages,
                    dependence_name="python",
                    dependence_version=python_version,
                    project_name=project.name,
                    project_url=project.web_url,
                )

            for dependence_name in dependencies:
                dependence_version: str = self._get_dependence_version(
                    dependence_name=dependence_name,
                    poetry_lock_packages=poetry_lock_packages,
                )
                self._add_dependence_to_group_packages(
                    group_packages=group_packages,
                    dependence_name=dependence_name,
                    dependence_version=dependence_version,
                    project_name=project.name,
                    project_url=project.web_url,
                )

        return group_packages

    @staticmethod
    def _get_sorted_group_packages(group_packages: dict) -> Generator[GroupPackage, Any, None]:
        return (
            GroupPackage(
                package_name=package_name,
                package_version=version,
                projects=sorted(projects, key=lambda x: x["project_name"].lower()),
            )
            for package_name, versions in sorted(group_packages.items())
            for version, projects in sorted(
                {
                    version: sorted(projects, key=lambda x: x["project_name"].lower())
                    for version, projects in versions.items()
                }.items(),
                key=lambda x: parse_version("0") if x[0] == VERSION_UNKNOWN else parse_version(x[0]),
            )
        )

    @staticmethod
    def _get_poetry_lock_packages(file: str | None) -> dict:
        decoded_poetry_lock: dict = tomllib.loads(base64.b64decode(file).decode("utf-8")) if file else {}
        return {pkg["name"]: pkg["version"] for pkg in decoded_poetry_lock.get("package", [])}

    @staticmethod
    def _get_pyproject_toml_packages(file: str | None) -> set[str]:
        decoded_pyproject_toml: dict = tomllib.loads(base64.b64decode(file).decode("utf-8")) if file else {}
        poetry_section: dict = decoded_pyproject_toml.get("tool", {}).get("poetry", {})

        pyproject_toml_deps: set[str] = {
            *poetry_section.get("dependencies", {}),
            *poetry_section.get("dev-dependencies", {}),
            *chain.from_iterable(
                [group.get("dependencies", {}).keys() for group in poetry_section.get("group", {}).values()]
            ),
        }
        with suppress(KeyError):
            pyproject_toml_deps.remove("python")

        return pyproject_toml_deps

    @staticmethod
    def _get_python_version(dockerfile: str) -> str:
        decoded_dockerfile: str = base64.b64decode(dockerfile).decode("utf-8")
        python_version = re.search(r"(?<=python:)\d+.\d+.?\d*", decoded_dockerfile)
        return python_version.group() if python_version else VERSION_UNKNOWN

    @staticmethod
    def _add_dependence_to_group_packages(
        group_packages: defaultdict,
        dependence_name: str,
        dependence_version: str,
        project_name: str,
        project_url: str,
    ) -> None:
        group_packages[dependence_name][dependence_version].append(
            {
                "project_name": project_name,
                "project_url": project_url,
            },
        )

    @staticmethod
    def _get_dependence_version(dependence_name: str, poetry_lock_packages: dict) -> str:
        for dep_name in (
            dependence_name,
            dependence_name.replace("-", "_"),
            dependence_name.replace("_", "-"),
        ):
            if dependence_version := poetry_lock_packages.get(dep_name):
                return dependence_version

        return VERSION_UNKNOWN
