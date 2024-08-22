from contextlib import suppress
from datetime import UTC, datetime
from typing import Any, TypedDict


class CachedFile(TypedDict):
    content: Any
    created_at: datetime


class FileCache:
    def __init__(self) -> None:
        self.file_cache: dict = {}

    def set(self, project_id: int, file_path: str, content: Any) -> None:
        self.file_cache.setdefault(project_id, {})[file_path] = CachedFile(
            content=content,
            created_at=datetime.now(tz=UTC),
        )

    def get(self, project_id: int, file_path: str) -> Any:
        file: CachedFile = self.file_cache.get(project_id, {}).get(file_path)
        return file["content"] if file is not None else None

    def get_created_at(self, project_id: int, file_path: str) -> datetime | None:
        file: CachedFile = self.file_cache.get(project_id, {}).get(file_path)
        return file["created_at"] if file is not None else None

    def delete(self, project_id: int, file_path: str) -> None:
        with suppress(KeyError):
            del self.file_cache[project_id][file_path]
