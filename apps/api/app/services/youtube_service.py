from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models.domain import ConnectedPlatform, Creator, SocialAccount
from app.integrations.youtube.public import (
    YouTubePublicClient,
    YouTubePublicError,
    compute_progress,
    next_actions,
)


class YouTubeService:
    def __init__(self, db: Session, client: YouTubePublicClient | None = None) -> None:
        self._db = db
        self._client = client or YouTubePublicClient()

    def get(self, creator: Creator) -> dict:
        row = self._row(creator)
        if row is None:
            social = self._primary_social(creator)
            if social is None:
                return {"connected": False, "platform": "youtube", "snapshot": None}
            return {"connected": True, "platform": "youtube", "snapshot": self._serialize_social(social)}
        return {"connected": True, "platform": "youtube", "snapshot": self._serialize(row)}

    def connect(self, creator: Creator, url: str) -> dict:
        try:
            snapshot = self._client.fetch_channel(url)
        except YouTubePublicError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return self._upsert(creator, snapshot)

    def refresh(self, creator: Creator) -> dict:
        row = self._row(creator)
        url = row.url if row else None
        if not url:
            social = self._primary_social(creator)
            url = social.profile_url if social else None
        if not url:
            raise HTTPException(status_code=404, detail="Connect a YouTube channel first.")
        return self.connect(creator, url)

    def sync_from_social(self, creator: Creator, social: SocialAccount) -> None:
        snapshot = dict(social.snapshot or {})
        if not snapshot.get("channel_id"):
            return
        self._upsert_connected(creator, snapshot, commit=False)
        self._db.commit()

    def _row(self, creator: Creator) -> ConnectedPlatform | None:
        return (
            self._db.query(ConnectedPlatform)
            .filter(ConnectedPlatform.creator_id == creator.id, ConnectedPlatform.platform == "youtube")
            .one_or_none()
        )

    def _primary_social(self, creator: Creator) -> SocialAccount | None:
        return (
            self._db.query(SocialAccount)
            .filter(SocialAccount.creator_id == creator.id, SocialAccount.platform == "YOUTUBE")
            .order_by(SocialAccount.created_at.asc())
            .first()
        )

    def _upsert(self, creator: Creator, snapshot: dict) -> dict:
        row = self._upsert_connected(creator, snapshot, commit=False)
        self._upsert_social(creator, snapshot)
        data = dict(creator.onboarding_data or {})
        data["youtube_url"] = snapshot.get("url")
        data["youtube_handle"] = snapshot.get("handle")
        creator.onboarding_data = data
        if snapshot.get("title") and creator.display_name in {"", "Creator"}:
            creator.display_name = snapshot["title"]
        self._db.commit()
        self._db.refresh(row)
        return {"connected": True, "platform": "youtube", "snapshot": self._serialize(row)}

    def _upsert_connected(self, creator: Creator, snapshot: dict, commit: bool = True) -> ConnectedPlatform:
        row = self._row(creator)
        now = datetime.now(UTC)
        if row is None:
            row = ConnectedPlatform(
                creator_id=creator.id,
                platform="youtube",
                external_id=snapshot["channel_id"],
                handle=snapshot.get("handle"),
                title=snapshot.get("title"),
                url=snapshot.get("url"),
                snapshot=snapshot,
                synced_at=now,
            )
            self._db.add(row)
        else:
            row.external_id = snapshot["channel_id"]
            row.handle = snapshot.get("handle")
            row.title = snapshot.get("title")
            row.url = snapshot.get("url")
            row.snapshot = snapshot
            row.synced_at = now
        if commit:
            self._db.commit()
            self._db.refresh(row)
        return row

    def _upsert_social(self, creator: Creator, snapshot: dict) -> SocialAccount:
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
            )
            self._db.add(row)
        row.account_name = snapshot.get("title")
        row.username = snapshot.get("handle")
        row.profile_url = snapshot.get("url")
        row.snapshot = snapshot
        row.last_synced_at = now
        row.connected_at = row.connected_at or now
        row.last_error = None
        return row

    def _serialize(self, row: ConnectedPlatform) -> dict:
        snapshot = dict(row.snapshot or {})
        snapshot["progress"] = compute_progress(snapshot.get("subscriber_count"), snapshot.get("video_count"))
        snapshot["next_actions"] = next_actions(snapshot)
        snapshot["synced_at"] = row.synced_at.isoformat() if row.synced_at else None
        snapshot["title"] = row.title or snapshot.get("title")
        snapshot["handle"] = row.handle or snapshot.get("handle")
        snapshot["url"] = row.url or snapshot.get("url")
        return snapshot

    def _serialize_social(self, row: SocialAccount) -> dict:
        snapshot = dict(row.snapshot or {})
        snapshot["progress"] = compute_progress(snapshot.get("subscriber_count"), snapshot.get("video_count"))
        snapshot["next_actions"] = next_actions(snapshot)
        snapshot["synced_at"] = row.last_synced_at.isoformat() if row.last_synced_at else None
        snapshot["title"] = row.account_name or snapshot.get("title")
        snapshot["handle"] = row.username or snapshot.get("handle")
        snapshot["url"] = row.profile_url or snapshot.get("url")
        return snapshot
