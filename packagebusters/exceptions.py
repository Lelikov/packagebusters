"""Packagebusters error models."""

from enum import IntEnum
from typing import Final

from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel


BODY_ERRORS: Final[dict] = {}
# pylint: disable=invalid-name


class ErrorModel(BaseModel):
    type: str = "dummy"
    detail: str
    error_code: int


class ErrCode(IntEnum):
    """Internal error codes."""

    BadRequest = 1
    BadGitlabGroupId = 2


class BadRequestError(HTTPException):
    """400."""

    def __init__(self, detail: dict) -> None:
        super().__init__(status_code=400, detail=detail)


class ForbiddenError(HTTPException):
    """403."""

    def __init__(self, detail: dict) -> None:
        super().__init__(status_code=403, detail=detail)


class NotFoundError(HTTPException):
    """404."""

    def __init__(self, detail: dict) -> None:
        super().__init__(status_code=404, detail=detail)


class ConflictError(HTTPException):
    """409."""

    def __init__(self, detail: dict) -> None:
        super().__init__(status_code=409, detail=detail)


class InternalServerError(HTTPException):
    """500."""

    def __init__(self, detail: dict) -> None:
        super().__init__(status_code=500, detail=detail)


class BadGitlabGroupIdError(BadRequestError):
    def __init__(self, group_id: int) -> None:
        super().__init__(detail={"detail": f"Group {group_id} not found", "error_code": ErrCode.BadGitlabGroupId})


def _make_detail(loc: tuple[str], err_msg: str) -> str:
    return " ".join(str(location) for location in loc) + " " + err_msg


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:  # pragma: no cover
    """HTTP exception handling and return valid JSON format response It's interesting case 'cause exc.detail type is.

    Any, and not str as mypy states.
    """
    if isinstance(exc.detail, str):
        err = ErrorModel(detail=exc.detail, error_code=0, type="")
    else:
        err = ErrorModel(**exc.detail)  # type: ignore[attr-defined]

    logger.error(
        f"{request.url.path} response error: {err.detail}, error_code: {err.error_code}",
    )

    return JSONResponse(status_code=exc.status_code, content=err.model_dump())
