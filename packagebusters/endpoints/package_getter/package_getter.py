from asyncio import to_thread
from typing import Final

from fastapi import APIRouter, Query
from loguru import logger

from .interfaces import IGroupPackage, IPackageGetter
from .types import GroupPackage, Project


class PackageGetterEndpoint:
    def __init__(self, package_getter: IPackageGetter) -> None:
        self.router: Final[APIRouter] = APIRouter()
        self.router.add_api_route(
            "/groups/{group_id}/packages",
            self.__call__,
            methods=["GET"],
            status_code=200,
        )
        self.package_getter = package_getter

    async def __call__(
        self,
        group_id: int,
        with_transitive_dependencies: bool = Query(default=False),
        is_cached: bool = Query(default=True),
    ) -> list[GroupPackage]:
        logger.debug(f"Get packages for group {group_id}")
        group_packages: list[IGroupPackage] = await to_thread(
            self.package_getter.get_group_packages,
            group_id=group_id,
            is_add_transitive_dependencies=with_transitive_dependencies,
            is_cached=is_cached,
        )

        return [
            GroupPackage(
                package_name=package["package_name"],
                package_version=package["package_version"],
                projects=[
                    Project(
                        project_name=project["project_name"],
                        project_url=project["project_url"],
                    )
                    for project in package["projects"]
                ],
            )
            for package in group_packages
        ]
