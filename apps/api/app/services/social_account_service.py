from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.token_crypto import encrypt_secret
from app.db.models.domain import AnalyticsSnapshot, Creator, SocialAccount
from app.integrations.social.adapter import PlatformNotConfiguredError
from app.integrations.social.registry import SocialPlatformService
from app.integrations.youtube.public import YouTubePublicClient, YouTubePublicError, compute_progress, next_actions
from app.services.youtube_service import YouTubeService

SUPPORTED = {"YOUTUBE", "INSTAGRAM", "FACEBOOK"}


class SocialAccountService:
    def __init__(self, db: Session, settings: Settings | None = None) -> None:
        self._db = db
        self._settings = settings or get_settings()
        self._platforms = SocialPlatformService(self._settings)

    def platform_statuses(self) -> list[dict]:
        return self._platforms.statuses()

    def list_accounts(self, creator: Creator) -> list[dict]:
        rows = (
            self._db.query(SocialAccount)
            .filter(SocialAccount.creator_id == creator.id)
            .order_by(SocialAccount.created_at.asc())
            .all()
        )
        return [self.serialize(row) for row in rows]

    def get_owned(self, creator: Creator, account_id: UUID) -> SocialAccount:
        row = (
            self._db.query(SocialAccount)
            .filter(SocialAccount.id == account_id, SocialAccount.creator_id == creator.id)
            .one_or_none()
        )
        if row is None:
            raise HTTPException(status_code=404, detail="Social account not found.")
        return row

    def connect(self, creator: Creator, platform: str, url: str | None = None) -> dict:
        key = platform.upper()
        if key not in SUPPORTED:
            raise HTTPException(status_code=400, detail=f"{platform} is not supported yet.")
        if key == "YOUTUBE":
            if not url:
                raise HTTPException(
                    status_code=400,
                    detail="Provide a public YouTube channel URL, or use OAuth when Google credentials are configured.",
                )
            return self._connect_youtube_public(creator, url)
        status = self._platforms.adapter(key).configuration_status()
        raise HTTPException(
            status_code=503,
            detail=status.get("message") or f"{key.title()} integration is not configured.",
        )

    def oauth_start(self, platform: str) -> dict:
        key = platform.upper()
        if key not in SUPPORTED:
            raise HTTPException(status_code=400, detail=f"{platform} is not supported yet.")
        adapter = self._platforms.adapter(key)
        status = adapter.configuration_status()
        if not status.get("oauth_ready"):
            raise HTTPException(
                status_code=503,
                detail=status.get("message") or f"{key.title()} integration is not configured.",
            )
        try:
            return adapter.connect()
        except PlatformNotConfiguredError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    def refresh(self, creator: Creator, account_id: UUID) -> dict:
        row = self.get_owned(creator, account_id)
        if row.platform == "YOUTUBE" and row.profile_url:
            try:
                snapshot = YouTubePublicClient().fetch_channel(row.profile_url)
            except YouTubePublicError as exc:
                row.last_error = str(exc)
                self._db.commit()
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            self._apply_youtube_snapshot(row, snapshot)
            self._store_metrics(creator, row, snapshot)
            self._db.commit()
            self._db.refresh(row)
            YouTubeService(self._db).sync_from_social(creator, row)
            return self.serialize(row)
        status = self._platforms.adapter(row.platform).configuration_status()
        raise HTTPException(
            status_code=503,
            detail=status.get("message") or f"{row.platform.title()} integration is not configured.",
        )

    def disconnect(self, creator: Creator, account_id: UUID) -> dict:
        row = self.get_owned(creator, account_id)
        platform = row.platform
        self._db.delete(row)
        self._db.commit()
        return {"disconnected": True, "platform": platform}

    def serialize(self, row: SocialAccount) -> dict:
        snapshot = dict(row.snapshot or {})
        if row.platform == "YOUTUBE":
            snapshot["progress"] = compute_progress(
                snapshot.get("subscriber_count"), snapshot.get("video_count")
            )
            snapshot["next_actions"] = next_actions(snapshot)
        payload = {
            "id": str(row.id),
            "platform": row.platform,
            "external_account_id": row.external_account_id,
            "account_name": row.account_name,
            "username": row.username,
            "account_type": row.account_type,
            "profile_url": row.profile_url,
            "avatar_url": row.avatar_url,
            "scopes": row.scopes or [],
            "connection_status": row.connection_status,
            "connected_at": row.connected_at.isoformat() if row.connected_at else None,
            "last_synced_at": row.last_synced_at.isoformat() if row.last_synced_at else None,
            "last_error": row.last_error,
            "has_oauth_tokens": bool(row.access_token_encrypted),
            "snapshot": snapshot or None,
        }
        return payload

    def store_tokens(self, row: SocialAccount, access: str | None, refresh: str | None) -> None:
        row.access_token_encrypted = encrypt_secret(access, self._settings.secret_key)
        row.refresh_token_encrypted = encrypt_secret(refresh, self._settings.secret_key)

    def _connect_youtube_public(self, creator: Creator, url: str) -> dict:
        try:
            snapshot = YouTubePublicClient().fetch_channel(url)
        except YouTubePublicError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        external_id = str(snapshot["channel_id"])
        row = (
            self._db.query(SocialAccount)
            .filter(
                SocialAccount.creator_id == creator.id,
                SocialAccount.platform == "YOUTUBE",
                SocialAccount.external_account_id == external_id,
            )
            .one_or_none()
        )
        now = datetime.now(UTC)
        if row is None:
            row = SocialAccount(
                creator_id=creator.id,
                platform="YOUTUBE",
                external_account_id=external_id,
                account_type="CHANNEL",
                connection_status="PUBLIC_SNAPSHOT",
                scopes=[],
                snapshot={},
            )
            self._db.add(row)
        self._apply_youtube_snapshot(row, snapshot)
        row.connected_at = row.connected_at or now
        row.last_error = None
        self._store_metrics(creator, row, snapshot)
        self._db.commit()
        self._db.refresh(row)
        YouTubeService(self._db).sync_from_social(creator, row)
        return self.serialize(row)

    def _apply_youtube_snapshot(self, row: SocialAccount, snapshot: dict) -> None:
        now = datetime.now(UTC)
        row.account_name = snapshot.get("title")
        row.username = snapshot.get("handle")
        row.profile_url = snapshot.get("url")
        row.avatar_url = snapshot.get("avatar_url")
        row.snapshot = snapshot
        row.last_synced_at = now
        row.connection_status = "PUBLIC_SNAPSHOT"

    def _store_metrics(self, creator: Creator, row: SocialAccount, snapshot: dict) -> None:
        for name, value in (
            ("followers", snapshot.get("subscriber_count")),
            ("content_count", snapshot.get("video_count")),
        ):
            if value is None:
                continue
            self._db.add(
                AnalyticsSnapshot(
                    creator_id=creator.id,
                    social_account_id=row.id,
                    platform=row.platform,
                    metric_name=name,
                    metric_value=str(value),
                    period="latest",
                    source="youtube_public",
                    raw_data={"metric": name},
                )
            )
