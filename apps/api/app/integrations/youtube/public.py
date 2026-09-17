from __future__ import annotations

import re
from typing import Any

import httpx

INNERTUBE_URL = "https://www.youtube.com/youtubei/v1"
CLIENT_CONTEXT = {
    "client": {
        "clientName": "WEB",
        "clientVersion": "2.20260916.01.00",
        "hl": "en",
        "gl": "IN",
    }
}
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Jadon Family creatorOS; public channel snapshot)",
}

SUBSCRIBER_MILESTONES = [100, 1_000, 10_000, 100_000, 1_000_000]


class YouTubePublicError(RuntimeError):
    pass


def normalize_channel_url(value: str) -> str:
    text = value.strip()
    if not text:
        raise YouTubePublicError("Enter a YouTube channel URL or @handle.")
    if text.startswith("@"):
        return f"https://www.youtube.com/{text}"
    if re.fullmatch(r"[\w.-]+", text) and "youtube" not in text.lower():
        return f"https://www.youtube.com/@{text}"
    if text.startswith("youtube.com"):
        text = "https://" + text
    if "youtu.be" in text or "youtube.com" in text:
        return text
    raise YouTubePublicError("Use a youtube.com channel URL or @handle.")


def parse_compact_count(text: str | None) -> int | None:
    if not text:
        return None
    match = re.search(r"([\d,.]+)\s*([KMB])?", text.replace("\xa0", " "), re.I)
    if not match:
        return None
    number = float(match.group(1).replace(",", ""))
    suffix = (match.group(2) or "").upper()
    multiplier = {"": 1, "K": 1_000, "M": 1_000_000, "B": 1_000_000_000}[suffix]
    return int(number * multiplier)


def _walk(obj: Any):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from _walk(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk(item)


def _header_stats(payload: dict[str, Any]) -> tuple[int | None, int | None, str | None, str | None]:
    subscribers = None
    videos = None
    subscribers_label = None
    videos_label = None
    for node in _walk(payload.get("header", {})):
        text = ""
        if isinstance(node.get("content"), str):
            text = node["content"]
        if (text.lower().endswith("subscribers") or text.lower().endswith("subscriber")) and subscribers is None:
            subscribers = parse_compact_count(text)
            subscribers_label = text
        if re.search(r"\d[\d,.]*\s*videos?\b", text, re.I) and videos is None:
            videos = parse_compact_count(text)
            videos_label = text
    return subscribers, videos, subscribers_label, videos_label


def _extract_videos(payload: dict[str, Any], channel_title: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for node in _walk(payload):
        lockup = node.get("lockupViewModel") if isinstance(node, dict) else None
        if not isinstance(lockup, dict):
            continue
        meta = lockup.get("metadata", {}).get("lockupMetadataViewModel", {})
        title = (meta.get("title") or {}).get("content")
        if not title:
            continue
        stats: list[str] = []
        for row in ((meta.get("metadata") or {}).get("contentMetadataViewModel") or {}).get(
            "metadataRows", []
        ):
            for part in row.get("metadataParts", []):
                content = ((part.get("text") or {}).get("content") or "").strip()
                if content:
                    stats.append(content)
        if not any(re.search(r"\d[\d,.]*\s*views?\b", stat, re.I) for stat in stats):
            continue
        video_id = None
        for inner in _walk(lockup):
            watch = inner.get("watchEndpoint") if isinstance(inner, dict) else None
            if isinstance(watch, dict) and watch.get("videoId"):
                video_id = watch["videoId"]
                break
        if not video_id or video_id in seen:
            continue
        seen.add(video_id)
        thumb = None
        for inner in _walk(lockup.get("contentImage", {})):
            if inner.get("url") and "ytimg.com" in str(inner.get("url")):
                thumb = inner["url"]
                break
        view_label = next((stat for stat in stats if re.search(r"\d[\d,.]*\s*views?\b", stat, re.I)), None)
        published = next((stat for stat in stats if "ago" in stat.lower()), None)
        items.append(
            {
                "video_id": video_id,
                "title": title,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "views": parse_compact_count(view_label),
                "views_label": view_label,
                "published_label": published,
                "thumbnail_url": thumb,
                "channel_title": channel_title,
            }
        )
    return items[:24]


def compute_progress(subscriber_count: int | None, video_count: int | None) -> dict[str, Any]:
    current = subscriber_count or 0
    next_goal = next((mark for mark in SUBSCRIBER_MILESTONES if mark > current), SUBSCRIBER_MILESTONES[-1])
    previous = 0
    for mark in SUBSCRIBER_MILESTONES:
        if mark <= current:
            previous = mark
        else:
            break
    span = max(next_goal - previous, 1)
    percent = min(100, int(((current - previous) / span) * 100))
    return {
        "metric": "subscribers",
        "current": current,
        "previous_milestone": previous,
        "next_milestone": next_goal,
        "percent": percent,
        "videos": video_count or 0,
    }


def next_actions(snapshot: dict[str, Any]) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    subs = snapshot.get("subscriber_count") or 0
    videos = snapshot.get("video_count") or 0
    items = snapshot.get("videos") or []
    description = (snapshot.get("description") or "").strip()
    last = items[0] if items else None
    published = (last or {}).get("published_label") or ""

    if re.search(r"year|month", published, re.I) or videos == 0:
        actions.append(
            {
                "id": "posting_habit",
                "title": "Restart a posting habit",
                "detail": (
                    "Public uploads look inactive. Post 1 searchable video or Short weekly for 8 weeks."
                ),
            }
        )
    if last and (
        "#" in (last.get("title") or "")
        or re.match(r"^\d{1,2}\s+\w+", last.get("title") or "")
        or len(last.get("title") or "") < 12
    ):
        actions.append(
            {
                "id": "titles",
                "title": "Use searchable titles",
                "detail": (
                    "Lead with the topic a viewer would type. Hashtag-first titles hide videos from search."
                ),
            }
        )
    if not description:
        actions.append(
            {
                "id": "about",
                "title": "Write a 3-line About section",
                "detail": "Say who you help, what you post, and how often. Empty About pages convert poorly.",
            }
        )
    if subs < 100:
        actions.append(
            {
                "id": "first_100",
                "title": "Aim at the first 100 subscribers",
                "detail": (
                    f"Public count is {subs}. Pin your clearest video and share each upload once. "
                    "This is a checkpoint, not a guarantee."
                ),
            }
        )
    if videos and videos < 12:
        actions.append(
            {
                "id": "series",
                "title": "Turn uploads into a series",
                "detail": "A named series with numbered parts is easier to follow than unrelated one-offs.",
            }
        )
    actions.append(
        {
            "id": "honesty",
            "title": "Measure in YouTube Studio",
            "detail": (
                "Public snapshot covers name, subs, and listed videos. Studio metrics need YouTube OAuth. "
                "Growth is not guaranteed."
            ),
        }
    )
    return actions[:6]


class YouTubePublicClient:
    def __init__(self, timeout: float = 25.0) -> None:
        self._timeout = timeout

    def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        try:
            with httpx.Client(timeout=self._timeout, headers=HEADERS) as client:
                response = client.post(f"{INNERTUBE_URL}/{path}", json={"context": CLIENT_CONTEXT, **body})
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            raise YouTubePublicError("Could not reach YouTube to load this channel.") from exc

    def fetch_channel(self, raw_url: str) -> dict[str, Any]:
        url = normalize_channel_url(raw_url)
        resolved = self._post("navigation/resolve_url", {"url": url})
        browse = (resolved.get("endpoint") or {}).get("browseEndpoint") or {}
        browse_id = browse.get("browseId")
        if not browse_id:
            raise YouTubePublicError("That URL did not resolve to a YouTube channel.")
        payload = self._post("browse", {"browseId": browse_id})
        meta = payload.get("metadata", {}).get("channelMetadataRenderer") or {}
        title = (meta.get("title") or "").strip() or "YouTube channel"
        description = meta.get("description") or ""
        vanity = meta.get("vanityChannelUrl") or url
        handle = None
        match = re.search(r"@[\w.-]+", vanity)
        if match:
            handle = match.group(0)
        subscribers, videos, sub_label, video_label = _header_stats(payload)
        video_items = _extract_videos(payload, title)
        if videos is None:
            videos = len(video_items)
        snapshot = {
            "platform": "youtube",
            "channel_id": browse_id,
            "title": title,
            "handle": handle,
            "url": vanity if vanity.startswith("http") else url,
            "description": description[:2000],
            "subscriber_count": subscribers,
            "subscriber_label": sub_label,
            "video_count": videos,
            "video_label": video_label,
            "videos": video_items,
        }
        snapshot["progress"] = compute_progress(subscribers, videos)
        snapshot["next_actions"] = next_actions(snapshot)
        snapshot["source"] = "youtube_public"
        snapshot["note"] = (
            "Public YouTube snapshot (channel page). Not Studio analytics. "
            "Connecting a URL is not a YouTube login and cannot publish or read private stats."
        )
        return snapshot
