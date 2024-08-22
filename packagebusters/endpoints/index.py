from typing import Any, Final

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


class IndexEndpoint:
    def __init__(self, templates: Jinja2Templates) -> None:
        self.templates: Final[Jinja2Templates] = templates
        self.router: Final[APIRouter] = APIRouter()
        self.router.add_api_route(
            "/",
            self.__call__,
            methods=["GET"],
            include_in_schema=False,
            status_code=200,
        )

    async def __call__(self, request: Request) -> Any:
        return self.templates.TemplateResponse("index.html", {"request": request})
