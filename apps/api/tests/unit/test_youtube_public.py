from app.integrations.youtube.public import (
    compute_progress,
    next_actions,
    normalize_channel_url,
    parse_compact_count,
)


def test_normalize_handle() -> None:
    assert normalize_channel_url("@laxminarayan308") == "https://www.youtube.com/@laxminarayan308"
    assert "laxminarayan308" in normalize_channel_url("https://www.youtube.com/@laxminarayan308")


def test_parse_compact_count() -> None:
    assert parse_compact_count("2 subscribers") == 2
    assert parse_compact_count("1.2K subscribers") == 1200
    assert parse_compact_count("3 views") == 3


def test_progress_and_actions() -> None:
    progress = compute_progress(2, 2)
    assert progress["next_milestone"] == 100
    assert progress["current"] == 2
    actions = next_actions(
        {
            "subscriber_count": 2,
            "video_count": 2,
            "description": "",
            "videos": [{"title": "Viral clip #tranding", "published_label": "3 years ago"}],
        }
    )
    ids = {item["id"] for item in actions}
    assert "posting_habit" in ids
    assert "about" in ids
    assert "honesty" in ids
