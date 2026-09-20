from typing import Any

from app.integrations.social.adapter import PlatformNotConfiguredError, SocialPlatformAdapter
from app.integrations.youtube.public import YouTubePublicClient, YouTubePublicError


class YouTubeAdapter(SocialPlatformAdapter):
    platform = "YOUTUBE"

    def is_configured(self) -> bool:
        return bool(self._settings.google_client_id.strip() and self._settings.google_client_secret.strip())

    def configuration_status(self) -> dict[str, Any]:
        oauth = self.is_configured()
        return {
            "platform": self.platform,
            "configured": True,
            "oauth_ready": oauth,
            "public_channel_lookup": True,
            "message": None
            if oauth
            else (
                "YouTube OAuth is not configured. You can still attach a public channel URL. "
                "Official analytics and publishing need GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."
            ),
        }

    def connect(self) -> dict[str, Any]:
        if not self.is_configured():
            raise PlatformNotConfiguredError("YouTube")
        raise PlatformNotConfiguredError(
            "YouTube",
            "YouTube OAuth credentials are present but the OAuth handshake is not enabled in this environment.",
        )

    def get_profile(self, account: Any) -> dict[str, Any]:
        url = getattr(account, "profile_url", None)
        if not url:
            raise PlatformNotConfiguredError("YouTube", "This YouTube account has no public URL to refresh.")
        try:
            return YouTubePublicClient().fetch_channel(url)
        except YouTubePublicError as exc:
            raise PlatformNotConfiguredError("YouTube", str(exc)) from exc

    def publish(self, account: Any, payload: dict[str, Any]) -> dict[str, Any]:
        raise PlatformNotConfiguredError("YouTube")


class InstagramAdapter(SocialPlatformAdapter):
    platform = "INSTAGRAM"

    def is_configured(self) -> bool:
        return bool(self._settings.meta_app_id.strip() and self._settings.meta_app_secret.strip())


class FacebookAdapter(SocialPlatformAdapter):
    platform = "FACEBOOK"

    def is_configured(self) -> bool:
        return bool(self._settings.meta_app_id.strip() and self._settings.meta_app_secret.strip())

    def configuration_status(self) -> dict[str, Any]:
        configured = self.is_configured()
        return {
            "platform": self.platform,
            "configured": configured,
            "oauth_ready": configured,
            "message": None
            if configured
            else "Facebook integration is not configured. Facebook Page OAuth requires META_APP_ID and META_APP_SECRET.",
        }


class SocialPlatformService:
    def __init__(self, settings: Any) -> None:
        self._adapters = {
            "YOUTUBE": YouTubeAdapter(settings),
            "INSTAGRAM": InstagramAdapter(settings),
            "FACEBOOK": FacebookAdapter(settings),
        }

    def adapter(self, platform: str) -> SocialPlatformAdapter:
        key = platform.upper()
        if key not in self._adapters:
            raise PlatformNotConfiguredError(platform, f"{platform} is not supported yet.")
        return self._adapters[key]

    def statuses(self) -> list[dict[str, Any]]:
        return [adapter.configuration_status() for adapter in self._adapters.values()]
