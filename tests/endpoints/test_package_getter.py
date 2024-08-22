from collections.abc import Callable
from typing import Any

from packagebusters.endpoints.package_getter.interfaces import IGroupPackage, IProject
from packagebusters.endpoints.package_getter.package_getter import PackageGetterEndpoint


async def test_package_getter(test_client: Callable, mocker: Any, faker: Any) -> None:
    package_name: str = faker.pystr()
    package_version: str = faker.pystr()
    project_name: str = faker.pystr()
    project_url: str = faker.pystr()
    package_getter_mock: Any = mocker.Mock(
        **{
            "get_group_packages.return_value": [
                IGroupPackage(
                    package_name=package_name,
                    package_version=package_version,
                    projects=[IProject(project_name=project_name, project_url=project_url)],
                )
            ]
        },
    )

    endpoint: PackageGetterEndpoint = PackageGetterEndpoint(package_getter=package_getter_mock)
    group_id: int = faker.pyint()
    with_transitive_dependencies: int = faker.pybool()
    is_cached: int = faker.pybool()

    with test_client([endpoint.router]) as client:
        resp = await client.get(
            f"/groups/{group_id}/packages",
            params={
                "with_transitive_dependencies": with_transitive_dependencies,
                "is_cached": is_cached,
            },
        )
    assert resp.status_code == 200
    assert resp.json() == [
        {
            "package_name": package_name,
            "package_version": package_version,
            "projects": [{"project_name": project_name, "project_url": project_url}],
        }
    ]
    assert package_getter_mock.get_group_packages.mock_calls == [
        mocker.call(
            group_id=group_id,
            is_add_transitive_dependencies=with_transitive_dependencies,
            is_cached=is_cached,
        ),
    ]
