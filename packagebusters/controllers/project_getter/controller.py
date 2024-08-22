import itertools
from concurrent.futures import ThreadPoolExecutor, as_completed

from loguru import logger

from .interfaces import IGitLabClient, IGroupProject


class ProjectGetter:
    def __init__(self, gitlab_client: IGitLabClient) -> None:
        self.gitlab_client = gitlab_client

    def get_projects(self, group_id: int) -> list[IGroupProject]:
        logger.debug(f"Getting projects for group {group_id}")
        projects: list[IGroupProject] = list(
            self.gitlab_client.groups.get(group_id).projects.list(iterator=True, archived=False),
        )
        logger.debug(f"Received project ids {[project.id for project in projects]} for group {group_id}")
        return projects

    def batch_get_projects(self, group_ids: set[int]) -> list[IGroupProject]:
        with ThreadPoolExecutor() as executor:
            project_futures = {
                executor.submit(
                    self.get_projects,
                    group_id=group_id,
                )
                for group_id in group_ids
            }
        return list(itertools.chain.from_iterable(future.result() for future in as_completed(project_futures)))
