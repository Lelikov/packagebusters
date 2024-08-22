"""Packagebusters entrypoint service file."""

from bakery import bake
from fastapi import FastAPI
from fastapi.exceptions import StarletteHTTPException
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from packagebusters.config import Settings
from packagebusters.containers import PackagebustersContainer
from packagebusters.exceptions import http_exception_handler


async def startup() -> None:
    """Global initialization."""
    await bake(PackagebustersContainer.config)
    settings: Settings = PackagebustersContainer.config()
    logger.info(f"Settings: {settings}")

    await PackagebustersContainer.aopen()

    APP.mount("/static", PackagebustersContainer().static_files, "static")

    for kwargs in PackagebustersContainer.endpoint_includes():  # type: ignore[operator]
        APP.include_router(**kwargs)


async def shutdown() -> None:
    """Global shutdown."""
    await PackagebustersContainer.aclose()


APP: FastAPI = FastAPI(
    title="Packagebusters",
    description="Packagebusters self-service",
    docs_url="/api/v1/doc",
    on_startup=[startup],
    on_shutdown=[shutdown],
    exception_handlers={
        StarletteHTTPException: http_exception_handler,
    },
)


APP.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
