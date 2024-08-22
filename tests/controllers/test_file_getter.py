from types import SimpleNamespace
from typing import Any, cast

from gitlab import GitlabGetError

from packagebusters.controllers.file_getter.controller import FileGetter, ProjectFile
from packagebusters.controllers.file_getter.interfaces import IProjectFile


def test_file_getter(mocker: Any, faker: Any) -> None:
    project_id: int = faker.pyint()
    file_path: str = faker.file_name()
    content: str = faker.text()
    gitlab_client_mock: Any = mocker.Mock(
        **{
            "projects.get.return_value": mocker.Mock(
                **{"files.get.return_value": SimpleNamespace(content=content)},
            ),
        },
    )
    file_cache_mock: Any = mocker.Mock()
    file_getter: FileGetter = FileGetter(gitlab_client=gitlab_client_mock, file_cache=file_cache_mock)

    file = file_getter.get_file(project_id=project_id, file_path=file_path, is_cached=False)
    file = cast(IProjectFile, file)

    assert file.content == content
    assert gitlab_client_mock.projects.get.mock_calls == [
        mocker.call(project_id),
        mocker.call().files.get(file_path=file_path, ref="master"),
    ]
    assert file_cache_mock.set.mock_calls == [
        mocker.call(
            project_id=project_id,
            file_path=file_path,
            content=ProjectFile(file.content),
        ),
    ]


def test_batch_get_files(mocker: Any, faker: Any) -> None:
    file_path: str = faker.file_name()
    first_project = SimpleNamespace(id=faker.pyint(), name=faker.pystr(), web_url=faker.url())
    second_project = SimpleNamespace(id=faker.pyint(), name=faker.pystr(), web_url=faker.url())
    first_project_file = SimpleNamespace(content=faker.text())
    second_project_file = SimpleNamespace(content=faker.text())
    gitlab_client_mock: Any = mocker.Mock(
        **{
            "projects.get.return_value": mocker.Mock(
                **{
                    "files.get.side_effect": [
                        first_project_file,
                        second_project_file,
                    ]
                },
            ),
        },
    )
    file_cache_mock: Any = mocker.Mock()
    file_getter: FileGetter = FileGetter(gitlab_client=gitlab_client_mock, file_cache=file_cache_mock)
    files = file_getter.batch_get_files(
        projects=[first_project, second_project],
        file_path=file_path,
        is_cached=False,
    )

    assert len(files) == 2
    assert (first_project, first_project_file) in files
    assert (second_project, second_project_file) in files


def test_cached_file_getter(mocker: Any, faker: Any) -> None:
    project_id: int = faker.pyint()
    file_path: str = faker.file_name()
    content: str = faker.text()
    gitlab_client_mock: Any = mocker.Mock()
    file_cache_mock: Any = mocker.Mock(**{"get.return_value": SimpleNamespace(content=content)})
    file_getter: FileGetter = FileGetter(gitlab_client=gitlab_client_mock, file_cache=file_cache_mock)

    file = file_getter.get_file(project_id=project_id, file_path=file_path, is_cached=True)
    file = cast(IProjectFile, file)

    assert file.content == content
    assert gitlab_client_mock.call_count == 0
    assert file_cache_mock.get.mock_calls == [mocker.call(project_id=project_id, file_path=file_path)]


def test_not_found_in_cache_file_getter(mocker: Any, faker: Any) -> None:
    project_id: int = faker.pyint()
    file_path: str = faker.file_name()
    content: str = faker.text()
    gitlab_client_mock: Any = mocker.Mock(
        **{
            "projects.get.return_value": mocker.Mock(
                **{"files.get.return_value": SimpleNamespace(content=content)},
            ),
        },
    )
    file_cache_mock: Any = mocker.Mock(**{"get.return_value": None})
    file_getter: FileGetter = FileGetter(gitlab_client=gitlab_client_mock, file_cache=file_cache_mock)

    file = file_getter.get_file(project_id=project_id, file_path=file_path, is_cached=True)
    file = cast(IProjectFile, file)

    assert file.content == content
    assert gitlab_client_mock.projects.get.mock_calls == [
        mocker.call(project_id),
        mocker.call().files.get(file_path=file_path, ref="master"),
    ]
    assert file_cache_mock.set.mock_calls == [
        mocker.call(
            project_id=project_id,
            file_path=file_path,
            content=ProjectFile(file.content),
        ),
    ]
    assert file_cache_mock.get.mock_calls == [mocker.call(project_id=project_id, file_path=file_path)]


def test_file_not_found(faker: Any, mocker: Any) -> None:
    project_id: int = faker.pyint()
    file_path: str = faker.file_name()
    gitlab_client_mock: Any = mocker.Mock(
        **{
            "projects.get.return_value": mocker.Mock(
                **{"files.get.side_effect": GitlabGetError()},
            ),
        },
    )
    file_cache_mock: Any = mocker.Mock()
    file_getter: FileGetter = FileGetter(gitlab_client=gitlab_client_mock, file_cache=file_cache_mock)

    file: IProjectFile | None = file_getter.get_file(project_id=project_id, file_path=file_path, is_cached=False)

    assert file is None
    assert gitlab_client_mock.projects.get.mock_calls == [
        mocker.call(project_id),
        mocker.call().files.get(file_path=file_path, ref="master"),
    ]
    assert file_cache_mock.set.mock_calls == [
        mocker.call(
            project_id=project_id,
            file_path=file_path,
            content=ProjectFile(""),
        ),
    ]
