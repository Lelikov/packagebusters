"""Config."""

from typing import Final

from pydantic_settings import BaseSettings


SENSITIVE_VARIABLES: Final[tuple[str, ...]] = ("token", "_dsn", "password", "username")


class Settings(BaseSettings):
    """Packagebusters Settings."""

    gitlab_token: str
    gitlab_url: str = "https://gitlab.com/"
    gitlab_api_version: str = "4"

    def __str__(self) -> str:
        values: list[str] = []
        for variable, value_map in self.model_json_schema().get("properties", {}).items():
            if isinstance(value_map, dict):
                is_need_to_masked = value_map.get("mask") or self._get_is_need_to_masked(variable)
                fmt_value = "***" if is_need_to_masked else getattr(self, variable)
                values.append(f"{variable}: {fmt_value}")
        return ", ".join(values)

    @staticmethod
    def _get_is_need_to_masked(variable: str) -> bool:
        return any(char in variable for char in SENSITIVE_VARIABLES)

    def __repr__(self) -> str:
        return self.__str__()
