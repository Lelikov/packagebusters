from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any

from gitlab import GitlabGetError
from loguru import logger

from .interfaces import IFileCache, IGitLabClient, IProject, IProjectFile


@dataclass
class ProjectFile:
    content: Any


class FileGetter:
    def __init__(self, gitlab_client: IGitLabClient, file_cache: IFileCache) -> None:
        self.gitlab_client: IGitLabClient = gitlab_client
        self.file_cache: IFileCache = file_cache

    def get_file(self, project_id: int, file_path: str, is_cached: bool) -> IProjectFile | None:
        if is_cached:
            cached_file: IProjectFile = self.file_cache.get(project_id=project_id, file_path=file_path)
            if cached_file is not None:
                logger.debug(f"Received file {file_path} for project {project_id} from cache")
                return cached_file
            logger.debug(f"File {file_path} for project {project_id} not found in cache")

        logger.debug(f"Getting file {file_path} for project {project_id}")
        try:
            file: IProjectFile = self.gitlab_client.projects.get(project_id).files.get(
                file_path=file_path,
                ref="master",
            )
            logger.debug(f"Received file {file_path} for project {project_id}")
            self.file_cache.set(project_id=project_id, file_path=file_path, content=ProjectFile(content=file.content))
        except GitlabGetError:
            logger.debug(f"File {file_path} not found in project {project_id}")
            self.file_cache.set(project_id=project_id, file_path=file_path, content=ProjectFile(content=""))
            return None

        return file

    def batch_get_files(
        self, projects: list[IProject], file_path: str, is_cached: bool
    ) -> list[tuple[IProject, IProjectFile | None]]:
        projects_files: list[tuple[IProject, IProjectFile | None]] = []
        with ThreadPoolExecutor() as executor:
            file_futures = {
                executor.submit(
                    self.get_file,
                    project.id,
                    file_path,
                    is_cached,
                ): project
                for project in projects
            }
            for future in as_completed(file_futures):
                file: IProjectFile | None = future.result()
                project: IProject = file_futures[future]
                projects_files.append((project, file))
        return projects_files
