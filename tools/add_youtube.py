#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess

from advisor_lib import advisor_dir, load_json, raw_vtt_dir, youtube_id


def existing_youtube_ids(advisor: str) -> set[str]:
    path = advisor_dir(advisor) / "transcripts_clean.json"
    if not path.exists():
        return set()
    try:
        data = load_json(path)
    except Exception:
        return set()
    records = data if isinstance(data, list) else []
    return {str(item.get("youtube_id")) for item in records if isinstance(item, dict) and item.get("youtube_id")}


def main() -> None:
    parser = argparse.ArgumentParser(description="Download YouTube captions into an advisor folder and rebuild transcript JSON.")
    parser.add_argument("advisor")
    parser.add_argument("urls", nargs="+")
    args = parser.parse_args()

    existing_ids = existing_youtube_ids(args.advisor)
    urls = []
    for url in args.urls:
        video_id = youtube_id(url)
        if video_id and video_id in existing_ids:
            print(f"Skipping existing YouTube transcript: {url}")
            continue
        urls.append(url)

    if not urls:
        print("No new YouTube URLs to download.")
        return

    folder = raw_vtt_dir(args.advisor)
    command = [
        "yt-dlp",
        "--skip-download",
        "--write-subs",
        "--write-auto-subs",
        "--sub-lang",
        "en",
        "--sub-format",
        "vtt",
        "-o",
        str(folder / "%(title)s [%(id)s].%(ext)s"),
        *urls,
    ]
    subprocess.run(command, check=True)
    subprocess.run(["python3", "tools/vtt_to_json.py", args.advisor], check=True)


if __name__ == "__main__":
    main()
