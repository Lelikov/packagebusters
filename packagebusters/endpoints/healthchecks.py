from typing import Final

from fastapi import APIRouter


class HealthCheckEndpoint:
    def __init__(self) -> None:
        self.router: Final[APIRouter] = APIRouter()
        self.router.add_api_route(
            "/health",
            self.health_check,
            methods=["GET"],
            include_in_schema=False,
            status_code=200,
        )
        self.router.add_api_route(
            "/readiness",
            self.readiness_check,
            methods=["GET"],
            include_in_schema=False,
            status_code=200,
        )

    @staticmethod
    async def readiness_check() -> None:  # pragma: no cover
        return None

    @staticmethod
    async def health_check() -> None:  # pragma: no cover
        return None
