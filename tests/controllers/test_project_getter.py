from types import SimpleNamespace
from typing import Any

from packagebusters.controllers.project_getter.controller import ProjectGetter
from packagebusters.controllers.project_getter.interfaces import IGroupProject


def test_project_getter(faker: Any, mocker: Any) -> None:
    project_id: int = faker.pyint()
    project_name: str = faker.pystr()
    project_web_url: str = faker.pystr()
    gitlab_client_mock: Any = mocker.Mock(
        **{
            "groups.get.return_value": mocker.Mock(
                **{
                    "projects.list.return_value": [
                        SimpleNamespace(
                            id=project_id,
                            name=project_name,
                            web_url=project_web_url,
                        ),
                    ],
                },
            ),
        },
    )
    group_id: int = faker.pyint()
    project_getter: ProjectGetter = ProjectGetter(gitlab_client=gitlab_client_mock)

    projects: list[IGroupProject] = project_getter.get_projects(group_id=group_id)

    assert len(projects) == 1
    assert projects[0].id == project_id
    assert projects[0].name == project_name
    assert projects[0].web_url == project_web_url
    assert gitlab_client_mock.groups.get.mock_calls == [
        mocker.call(group_id),
        mocker.call().projects.list(iterator=True, archived=False),
    ]


def test_batch_get_project(faker: Any, mocker: Any) -> None:
    group_ids: set[int] = {faker.pyint() * 2}
    project_1: SimpleNamespace = SimpleNamespace(id=faker.pyint(), name=faker.pystr(), web_url=faker.pystr())
    project_2: SimpleNamespace = SimpleNamespace(id=faker.pyint(), name=faker.pystr(), web_url=faker.pystr())
    gitlab_client_mock: Any = mocker.Mock(
        **{
            "groups.get.return_value": mocker.Mock(
                **{
                    "projects.list.side_effect": [[project_1, project_2]],
                },
            ),
        },
    )

    project_getter: ProjectGetter = ProjectGetter(gitlab_client=gitlab_client_mock)

    projects: list[IGroupProject] = project_getter.batch_get_projects(group_ids=group_ids)

    assert len(projects) == 2
    assert project_1 in projects
    assert project_2 in projects
