"""Packagebusters container worker."""

from bakery import Bakery, Cake
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from gitlab import Gitlab

from packagebusters.config import Settings
from packagebusters.controllers.cache.controller import FileCache
from packagebusters.controllers.file_getter.controller import FileGetter
from packagebusters.controllers.package_getter.controller import PackageGetter
from packagebusters.controllers.project_getter.controller import ProjectGetter
from packagebusters.controllers.subgroup_getter.controller import SubGroupGetter
from packagebusters.endpoints.healthchecks import HealthCheckEndpoint
from packagebusters.endpoints.index import IndexEndpoint
from packagebusters.endpoints.package_getter.package_getter import PackageGetterEndpoint


class PackagebustersContainer(Bakery):
    """Main Packagebusters container."""

    config: Settings = Cake(Settings)
    _file_cache: FileCache = FileCache()
    _gitlab_client: Gitlab = Cake(
        Cake(
            Gitlab,
            url=config.gitlab_url,
            private_token=config.gitlab_token,
            api_version=config.gitlab_api_version,
        ),
    )
    _subgroup_getter: SubGroupGetter = Cake(SubGroupGetter, gitlab_client=_gitlab_client)
    _project_getter: ProjectGetter = Cake(ProjectGetter, gitlab_client=_gitlab_client)
    _file_getter: FileGetter = Cake(FileGetter, gitlab_client=_gitlab_client, file_cache=_file_cache)

    _package_getter: PackageGetter = Cake(
        PackageGetter,
        subgroup_getter=_subgroup_getter,
        project_getter=_project_getter,
        file_getter=_file_getter,
    )

    templates: Jinja2Templates = Cake(Jinja2Templates, directory="templates")
    static_files: StaticFiles = Cake(StaticFiles, directory="templates/static")

    _health_endpoint: HealthCheckEndpoint = Cake(HealthCheckEndpoint)
    _index_endpoint: IndexEndpoint = Cake(IndexEndpoint, templates=templates)
    _package_getter_endpoint: PackageGetterEndpoint = Cake(
        PackageGetterEndpoint,  # type: ignore[arg-type]
        package_getter=_package_getter,  # type: ignore[arg-type]
    )

    endpoint_includes: list = Cake(
        [
            {"router": _health_endpoint.router, "prefix": "/check"},
            {"router": _package_getter_endpoint.router, "prefix": "/api/v1"},
            {"router": _index_endpoint.router},
        ],
    )
