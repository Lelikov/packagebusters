from datetime import UTC, datetime
from typing import Any

from freezegun import freeze_time

from packagebusters.controllers.cache.controller import FileCache


@freeze_time("1988-10-14")
def test_cache(faker: Any) -> None:
    project_id: int = faker.pyint()
    file_path: str = faker.file_name()
    content: str = faker.text()
    cache: FileCache = FileCache()

    for i in range(3):
        cache.set(project_id=project_id * i, file_path=file_path * i, content=content * i)
    cached_content: str | None = cache.get(project_id=project_id, file_path=file_path)
    cached_content_created_at: datetime | None = cache.get_created_at(project_id=project_id, file_path=file_path)

    assert cached_content == content
    assert cached_content_created_at == datetime(1988, 10, 14, tzinfo=UTC)

    cache.delete(project_id=project_id, file_path=file_path)
    cached_content: str = cache.get(project_id=project_id, file_path=file_path)

    assert cached_content is None
