"""Tests for Packagebusters config."""

from packagebusters.config import Settings
from tests.conftest import patch_settings_context


INSENSITIVE_SETTINGS: set[str] = {"gitlab_url", "gitlab_api_version"}


def test_config() -> None:
    """Test config."""
    unmasked_settings: set[str] = set()
    with patch_settings_context():
        for setting in str(Settings()).split(", "):
            key, value = setting.split(": ")
            if value != "***":
                unmasked_settings.add(key)

    assert unmasked_settings == INSENSITIVE_SETTINGS
