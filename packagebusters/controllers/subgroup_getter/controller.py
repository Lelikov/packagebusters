from gitlab import GitlabGetError
from loguru import logger

from packagebusters.exceptions import BadGitlabGroupIdError
from .interfaces import IGitLabClient, IGroupDescendantGroup


class SubGroupGetter:
    def __init__(self, gitlab_client: IGitLabClient) -> None:
        self.gitlab_client = gitlab_client

    def get_subgroup_ids(self, group_id: int) -> set[int]:
        logger.debug(f"Getting subgroups for group {group_id}")
        try:
            groups: list[IGroupDescendantGroup] = self.gitlab_client.groups.get(
                group_id,
                archived=False,
            ).descendant_groups.list(iterator=True)
        except GitlabGetError as exc:
            raise BadGitlabGroupIdError(group_id=group_id) from exc
        subgroup_ids: set = {group.id for group in groups}
        logger.debug(f"Received subgroups ids {subgroup_ids} for group {group_id}")
        return subgroup_ids
