from types import SimpleNamespace
from typing import Any

import pytest
from gitlab import GitlabGetError

from packagebusters.controllers.subgroup_getter.controller import SubGroupGetter
from packagebusters.exceptions import BadGitlabGroupIdError


def test_subgroup_getter(faker: Any, mocker: Any) -> None:
    subgroup_id: int = faker.pyint()
    gitlab_client_mock: Any = mocker.Mock(
        **{
            "groups.get.return_value": mocker.Mock(
                **{
                    "descendant_groups.list.return_value": [
                        SimpleNamespace(id=subgroup_id),
                        SimpleNamespace(id=subgroup_id + 1),
                    ],
                },
            ),
        },
    )
    group_id: int = faker.pyint()
    subgroup_getter: SubGroupGetter = SubGroupGetter(gitlab_client=gitlab_client_mock)

    subgroups: set[int] = subgroup_getter.get_subgroup_ids(group_id=group_id)

    assert subgroups == {subgroup_id, subgroup_id + 1}
    assert gitlab_client_mock.groups.get.mock_calls == [
        mocker.call(group_id, archived=False),
        mocker.call().descendant_groups.list(iterator=True),
    ]


def test_subgroup_getter_invalid_group(faker: Any, mocker: Any) -> None:
    gitlab_client_mock: Any = mocker.Mock(
        **{"groups.get.side_effect": GitlabGetError()},
    )
    group_id: int = faker.pyint()
    subgroup_getter: SubGroupGetter = SubGroupGetter(gitlab_client=gitlab_client_mock)

    with pytest.raises(BadGitlabGroupIdError, match=f"Group {group_id} not found"):
        subgroup_getter.get_subgroup_ids(group_id=group_id)
