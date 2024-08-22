from base64 import b64encode
from types import SimpleNamespace


POETRY_LOCK_PROJECT_0: SimpleNamespace = SimpleNamespace(
    content=b64encode(
        b"""
    [[package]]
    name = "common-package"
    version = "0.1.2"

    [[package]]
    name = "different_naming"
    version = "0.8.8"

    [[package]]
    name = "transitive_dependencies"
    version = "3.2.1"
    """,
    )
)

PYPROJECT_TOML_PROJECT_0: SimpleNamespace = SimpleNamespace(
    content=b64encode(
        b"""
    [tool.poetry.dependencies]
    python = ">=3.12,<3.13"
    common-package = "^0.1.1"

    [tool.poetry.group.ci.dependencies]
    unknown_package = { version = "^0.1.6", python = ">= 3.12"}

    [tool.poetry.group.dev.dependencies]
    different-naming = "^0.8.2"
    """,
    )
)

DOCKER_FILE_PROJECT_0: SimpleNamespace = SimpleNamespace(
    content=b64encode(
        b"""
    ARG BASE_IMAGE="artifactory/rust-community-docker/rust:1.77.1-slim-rbru"
    FROM ${BASE_IMAGE} AS deps
    """,
    )
)

POETRY_LOCK_PROJECT_1: SimpleNamespace = SimpleNamespace(
    content=b64encode(
        b"""
    [[package]]
    name = "common-package"
    version = "0.1.2"

    [[package]]
    name = "old-package"
    version = "8.8.8"
    """,
    )
)

PYPROJECT_TOML_PROJECT_1: SimpleNamespace = SimpleNamespace(
    content=b64encode(
        b"""
    [tool.poetry.dependencies]
    python = ">=3.12,<3.13"
    common-package = "^0.1.1"

    [tool.poetry.dev-dependencies]
    old-package = "^8.8.2"
    """,
    )
)

DOCKER_FILE_PROJECT_1: SimpleNamespace = SimpleNamespace(
    content=b64encode(
        b"""
    ARG BASE_IMAGE="artifactory/python-community-docker/python:3.12.2-slim-rbru"
    FROM ${BASE_IMAGE} AS deps
    """,
    )
)
