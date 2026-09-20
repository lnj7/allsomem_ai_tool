from abc import ABC, abstractmethod
from typing import Any

from app.core.config import Settings


class PlatformNotConfiguredError(RuntimeError):
    def __init__(self, platform: str, message: str | None = None) -> None:
        self.platform = platform
        super().__init__(message or f"{platform} integration is not configured.")


class SocialPlatformAdapter(ABC):
    platform: str

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @abstractmethod
    def is_configured(self) -> bool:
        raise NotImplementedError

    def configuration_status(self) -> dict[str, Any]:
        configured = self.is_configured()
        return {
            "platform": self.platform,
            "configured": configured,
            "oauth_ready": configured,
            "message": None
            if configured
            else f"{self.platform} integration is not configured.",
        }

    def connect(self) -> dict[str, Any]:
        raise PlatformNotConfiguredError(self.platform)

    def disconnect(self, account: Any) -> None:
        return None

    def refresh_token(self, account: Any) -> dict[str, Any]:
        raise PlatformNotConfiguredError(self.platform)

    def get_profile(self, account: Any) -> dict[str, Any]:
        raise PlatformNotConfiguredError(self.platform)

    def get_accounts(self) -> list[dict[str, Any]]:
        raise PlatformNotConfiguredError(self.platform)

    def get_posts(self, account: Any) -> list[dict[str, Any]]:
        raise PlatformNotConfiguredError(self.platform)

    def get_post(self, account: Any, post_id: str) -> dict[str, Any]:
        raise PlatformNotConfiguredError(self.platform)

    def publish(self, account: Any, payload: dict[str, Any]) -> dict[str, Any]:
        raise PlatformNotConfiguredError(self.platform)

    def schedule(self, account: Any, payload: dict[str, Any]) -> dict[str, Any]:
        raise PlatformNotConfiguredError(self.platform)

    def get_analytics(self, account: Any) -> dict[str, Any]:
        raise PlatformNotConfiguredError(self.platform)

    def get_audience(self, account: Any) -> dict[str, Any]:
        raise PlatformNotConfiguredError(self.platform)

    def get_comments(self, account: Any) -> list[dict[str, Any]]:
        raise PlatformNotConfiguredError(self.platform)
