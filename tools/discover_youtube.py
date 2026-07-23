#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from advisor_lib import advisor_dir, load_json, youtube_id


def existing_urls(advisor: str) -> set[str]:
    folder = advisor_dir(advisor)
    urls: set[str] = set()
    for filename in ("transcripts_clean.json", "sources.json"):
        path = folder / filename
        if not path.exists():
            continue
        try:
            data = load_json(path)
        except Exception:
            continue
        records = data if isinstance(data, list) else []
        for item in records:
            if not isinstance(item, dict):
                continue
            url = item.get("youtube_url") or item.get("url")
            if url:
                urls.add(str(url))
            video_id = item.get("youtube_id")
            if video_id:
                urls.add(f"https://www.youtube.com/watch?v={video_id}")
    return urls


def compact(value: str, max_len: int = 220) -> str:
    value = " ".join((value or "").split())
    if len(value) <= max_len:
        return value
    return value[:max_len].rsplit(" ", 1)[0] + "..."


def normalize_upload_date(value: str | None) -> str:
    if not value:
        return ""
    try:
        return datetime.strptime(value, "%Y%m%d").date().isoformat()
    except ValueError:
        return value


def search_youtube(query: str, limit: int) -> list[dict[str, str]]:
    command = [
        "yt-dlp",
        "--dump-json",
        "--flat-playlist",
        "--skip-download",
        f"ytsearch{limit}:{query}",
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    records: list[dict[str, str]] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        video_id = str(raw.get("id") or "")
        url = raw.get("webpage_url") or raw.get("url") or ""
        if video_id and not str(url).startswith("http"):
            url = f"https://www.youtube.com/watch?v={video_id}"
        records.append(
            {
                "title": str(raw.get("title") or url),
                "url": str(url),
                "date": normalize_upload_date(raw.get("upload_date")),
                "channel": str(raw.get("channel") or raw.get("uploader") or ""),
                "duration": str(raw.get("duration") or ""),
                "description": compact(str(raw.get("description") or "")),
            }
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover YouTube videos and append reviewable candidates to sources_todo.md.")
    parser.add_argument("advisor")
    parser.add_argument("--focus", required=True)
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--query", help="Override the default '<advisor> <focus>' YouTube search query.")
    args = parser.parse_args()

    query = args.query or f"{args.advisor} {args.focus}"
    folder = advisor_dir(args.advisor)
    todo = folder / "sources_todo.md"
    seen = existing_urls(args.advisor)
    records = search_youtube(query, args.limit)

    lines = []
    if todo.exists():
        lines.append(todo.read_text(encoding="utf-8", errors="ignore").rstrip())
        lines.append("")
    else:
        lines.extend([f"# Source Discovery: {args.advisor}", ""])

    lines.extend(
        [
            "## YouTube Candidates",
            "",
            f"Query: {query}",
            "",
        ]
    )
    added = 0
    for record in records:
        url = record["url"]
        video_key = youtube_id(url)
        canonical = f"https://www.youtube.com/watch?v={video_key}" if video_key else url
        if canonical in seen or url in seen:
            continue
        why = f"Potentially relevant to {args.focus}; review title, channel, date, and description before checking."
        lines.extend(
            [
                f"- [ ] {record['title']}",
                "  Type: youtube",
                f"  URL: {canonical}",
                f"  Date: {record['date']}",
                f"  Channel: {record['channel']}",
                f"  Duration: {record['duration']}",
                f"  Description: {record['description']}",
                f"  Why relevant: {why}",
                "",
            ]
        )
        added += 1

    todo.write_text("\n".join(lines), encoding="utf-8")
    print(f"Added {added} new YouTube candidates to {todo}")


if __name__ == "__main__":
    main()
