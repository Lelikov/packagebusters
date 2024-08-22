ARG BASE_IMAGE="python:3.12.5-slim"

FROM ${BASE_IMAGE} AS base

ENV HOME_PATH="/home/packagebusters"

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1

ENV PATH="${POETRY_HOME}/bin:${HOME_PATH}/.venv/bin:${PATH}"

WORKDIR ${HOME_PATH}

FROM base AS deps

RUN apt-get update && \
    apt-get install -y \
    curl

RUN --mount=type=cache,target=/root/.cache \
    curl -sSL https://install.python-poetry.org | python -

WORKDIR ${HOME_PATH}
COPY poetry.lock pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache \
    poetry config installer.max-workers 10 && \
    poetry config virtualenvs.in-project true && \
    poetry install

FROM deps AS development

RUN groupadd -g 1000 packagebusters \
    && useradd -u 1000 -g packagebusters \
    -d ${HOME_PATH} -m -s /bin/bash packagebusters
WORKDIR ${HOME_PATH}
USER packagebusters

COPY --from=deps --chown=1000:1000 ${HOME_PATH}/.venv ${HOME_PATH}/.venv
COPY --chown=1000:1000 packagebusters packagebusters
COPY --chown=1000:1000 templates templates

ENTRYPOINT ["uvicorn", "packagebusters.__main__:APP", "--host", "0.0.0.0", "--log-level", "warning", "--reload"]
