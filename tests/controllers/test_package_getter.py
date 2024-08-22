from collections.abc import Generator
from typing import Any
from unittest.mock import Mock

from packagebusters.controllers.package_getter.controller import PackageGetter
from packagebusters.controllers.package_getter.types import GroupPackage
from tests.fixtures.files import (
    DOCKER_FILE_PROJECT_0,
    DOCKER_FILE_PROJECT_1,
    POETRY_LOCK_PROJECT_0,
    POETRY_LOCK_PROJECT_1,
    PYPROJECT_TOML_PROJECT_0,
    PYPROJECT_TOML_PROJECT_1,
)
from tests.fixtures.mockers import get_mocked_projects


def test_package_getter(mocker: Any, faker: Any) -> None:
    subgroup_id: int = faker.pyint()
    group_id: int = subgroup_id + faker.pyint()
    is_cached: bool = faker.pybool()
    subgroup_getter_mock: Any = mocker.Mock(**{"get_subgroup_ids.return_value": {subgroup_id}})
    project_0, project_1 = get_mocked_projects(num_of_projects=2)
    project_getter_mock: Any = Mock(**{"batch_get_projects.return_value": [project_0, project_1]})
    file_getter_mock: Any = Mock(
        **{
            "batch_get_files.side_effect": [
                [(project_0, POETRY_LOCK_PROJECT_0), (project_1, POETRY_LOCK_PROJECT_1)],
                [(project_0, DOCKER_FILE_PROJECT_0), (project_1, DOCKER_FILE_PROJECT_1)],
                [(project_0, PYPROJECT_TOML_PROJECT_0), (project_1, PYPROJECT_TOML_PROJECT_1)],
            ]
        }
    )

    package_getter: PackageGetter = PackageGetter(
        subgroup_getter=subgroup_getter_mock,
        project_getter=project_getter_mock,
        file_getter=file_getter_mock,
    )

    group_packages: Generator[GroupPackage, Any, None] = package_getter.get_group_packages(
        group_id=group_id,
        is_add_transitive_dependencies=False,
        is_cached=is_cached,
    )

    assert list(group_packages) == [
        {
            "package_name": "common-package",
            "package_version": "0.1.2",
            "projects": [
                {"project_name": "test_project_0", "project_url": "https://test_project_0"},
                {"project_name": "test_project_1", "project_url": "https://test_project_1"},
            ],
        },
        {
            "package_name": "different-naming",
            "package_version": "0.8.8",
            "projects": [{"project_name": "test_project_0", "project_url": "https://test_project_0"}],
        },
        {
            "package_name": "old-package",
            "package_version": "8.8.8",
            "projects": [{"project_name": "test_project_1", "project_url": "https://test_project_1"}],
        },
        {
            "package_name": "python",
            "package_version": "Version Unknown",
            "projects": [{"project_name": "test_project_0", "project_url": "https://test_project_0"}],
        },
        {
            "package_name": "python",
            "package_version": "3.12.2",
            "projects": [{"project_name": "test_project_1", "project_url": "https://test_project_1"}],
        },
        {
            "package_name": "unknown_package",
            "package_version": "Version Unknown",
            "projects": [{"project_name": "test_project_0", "project_url": "https://test_project_0"}],
        },
    ]

    assert subgroup_getter_mock.get_subgroup_ids.mock_calls == [mocker.call(group_id=group_id)]
    assert project_getter_mock.batch_get_projects.mock_calls == [mocker.call(group_ids={group_id, subgroup_id})]
    assert file_getter_mock.batch_get_files.mock_calls == [
        mocker.call(projects=[project_0, project_1], file_path="poetry.lock", is_cached=is_cached),
        mocker.call(projects=[project_0, project_1], file_path="Dockerfile", is_cached=is_cached),
        mocker.call(projects=[project_0, project_1], file_path="pyproject.toml", is_cached=is_cached),
    ]


def test_package_getter_is_add_transitive_dependencies(mocker: Any, faker: Any) -> None:
    group_id: int = faker.pyint()
    is_cached: bool = faker.pybool()
    subgroup_getter_mock: Any = mocker.Mock(**{"get_subgroup_ids.return_value": {}})
    project_0: Any = get_mocked_projects(1)[0]
    project_getter_mock: Any = Mock(**{"batch_get_projects.return_value": [project_0]})
    file_getter_mock: Any = Mock(
        **{
            "batch_get_files.side_effect": [
                [(project_0, POETRY_LOCK_PROJECT_0)],
                [(project_0, None)],
            ]
        }
    )

    package_getter: PackageGetter = PackageGetter(
        subgroup_getter=subgroup_getter_mock,
        project_getter=project_getter_mock,
        file_getter=file_getter_mock,
    )

    group_packages: Generator[GroupPackage, Any, None] = package_getter.get_group_packages(
        group_id=group_id,
        is_add_transitive_dependencies=True,
        is_cached=is_cached,
    )

    assert list(group_packages) == [
        {
            "package_name": "common-package",
            "package_version": "0.1.2",
            "projects": [{"project_name": "test_project_0", "project_url": "https://test_project_0"}],
        },
        {
            "package_name": "different_naming",
            "package_version": "0.8.8",
            "projects": [{"project_name": "test_project_0", "project_url": "https://test_project_0"}],
        },
        {
            "package_name": "transitive_dependencies",
            "package_version": "3.2.1",
            "projects": [{"project_name": "test_project_0", "project_url": "https://test_project_0"}],
        },
    ]

    assert subgroup_getter_mock.get_subgroup_ids.mock_calls == [mocker.call(group_id=group_id)]
    assert project_getter_mock.batch_get_projects.mock_calls == [mocker.call(group_ids={group_id})]
    assert file_getter_mock.batch_get_files.mock_calls == [
        mocker.call(projects=[project_0], file_path="poetry.lock", is_cached=is_cached),
        mocker.call(projects=[project_0], file_path="Dockerfile", is_cached=is_cached),
    ]


def test_package_getter_wo_poetry_lock_in_project_0(mocker: Any, faker: Any) -> None:
    subgroup_id: int = faker.pyint()
    group_id: int = subgroup_id + faker.pyint()
    subgroup_getter_mock: Any = mocker.Mock(**{"get_subgroup_ids.return_value": {subgroup_id}})
    is_cached: bool = faker.pybool()
    project_0, project_1 = get_mocked_projects(num_of_projects=2)
    project_getter_mock: Any = Mock(**{"batch_get_projects.return_value": [project_0, project_1]})
    file_getter_mock: Any = Mock(
        **{
            "batch_get_files.side_effect": [
                [(project_0, None), (project_1, POETRY_LOCK_PROJECT_1)],
                [(project_1, None)],
            ]
        }
    )

    package_getter: PackageGetter = PackageGetter(
        subgroup_getter=subgroup_getter_mock,
        project_getter=project_getter_mock,
        file_getter=file_getter_mock,
    )

    group_packages: Generator[GroupPackage, Any, None] = package_getter.get_group_packages(
        group_id=group_id,
        is_add_transitive_dependencies=True,
        is_cached=is_cached,
    )

    assert list(group_packages) == [
        {
            "package_name": "common-package",
            "package_version": "0.1.2",
            "projects": [{"project_name": "test_project_1", "project_url": "https://test_project_1"}],
        },
        {
            "package_name": "old-package",
            "package_version": "8.8.8",
            "projects": [{"project_name": "test_project_1", "project_url": "https://test_project_1"}],
        },
    ]

    assert subgroup_getter_mock.get_subgroup_ids.mock_calls == [mocker.call(group_id=group_id)]
    assert project_getter_mock.batch_get_projects.mock_calls == [mocker.call(group_ids={group_id, subgroup_id})]
    assert file_getter_mock.batch_get_files.mock_calls == [
        mocker.call(projects=[project_0, project_1], file_path="poetry.lock", is_cached=is_cached),
        mocker.call(projects=[project_1], file_path="Dockerfile", is_cached=is_cached),
    ]
