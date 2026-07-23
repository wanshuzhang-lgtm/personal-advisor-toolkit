#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

from advisor_lib import advisor_dir, append_json_records, build_context_notes, fetch_url_text


CHECKBOX_RE = re.compile(r"^- \[(?P<checked>[ xX])\]\s+(?P<title>.+)")


def parse_checked(path: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        match = CHECKBOX_RE.match(line)
        if match:
            if current:
                items.append(current)
            current = {"title": match.group("title").strip()} if match.group("checked").lower() == "x" else None
            continue
        if current and ":" in line:
            key, value = line.strip().split(":", 1)
            current[key.lower().replace(" ", "_")] = value.strip()
    if current:
        items.append(current)
    return items


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest checked source candidates from sources_todo.md.")
    parser.add_argument("advisor")
    parser.add_argument("--todo", default="sources_todo.md")
    parser.add_argument("--execute-youtube", action="store_true", help="Run add_youtube.py for checked YouTube URLs.")
    parser.add_argument("--no-fetch-web", action="store_true", help="Do not auto-fetch checked non-YouTube web sources.")
    args = parser.parse_args()

    folder = advisor_dir(args.advisor)
    todo = folder / args.todo
    items = parse_checked(todo)
    saved: list[dict[str, str]] = []
    manual_needed: list[dict[str, str]] = []

    for item in items:
        source_type = item.get("type", "web")
        url = item.get("url", "")
        if source_type == "search":
            continue
        if source_type == "youtube" and args.execute_youtube:
            subprocess.run(["python3", "tools/add_youtube.py", args.advisor, url], check=False)
            continue
        text = ""
        fetch_error = ""
        should_fetch = bool(url and not args.no_fetch_web and source_type not in {"linkedin", "youtube"})
        if should_fetch:
            try:
                text = fetch_url_text(url)
            except Exception as exc:
                fetch_error = str(exc)
        if source_type == "linkedin":
            manual_needed.append({**item, "reason": "LinkedIn usually requires login or blocks automated fetching. Copy the post text into a local file and add it with tools/add_source.py --file."})
        elif url and not text.strip() and source_type not in {"youtube"}:
            reason = "Auto-fetch returned no text."
            if fetch_error:
                reason = f"Auto-fetch failed: {fetch_error}"
            if args.no_fetch_web:
                reason = "Auto-fetch was disabled with --no-fetch-web."
            manual_needed.append({**item, "reason": reason})
        saved.append(
            {
                "title": item.get("title", url),
                "type": source_type,
                "url": url,
                "date": item.get("date", ""),
                "why_relevant": item.get("why_relevant", ""),
                "capture_status": "text_saved" if text.strip() else "metadata_only",
                "text": text,
            }
        )

    if saved:
        output = folder / "sources.json"
        append_json_records(output, saved)
        notes = build_context_notes(args.advisor)
        print(f"Saved {len(saved)} metadata/source records to {output}")
        print(f"Updated {notes}")
    else:
        print("No checked ingestible sources found.")

    if manual_needed:
        print("\nManual action needed for these sources:")
        for item in manual_needed:
            print(f"- {item.get('title', item.get('url', 'Untitled'))}")
            print(f"  URL: {item.get('url', '')}")
            print(f"  Reason: {item.get('reason', '')}")
            print("  Next: copy the source text to a .txt file, then run:")
            print(
                f"    python3 tools/add_source.py {args.advisor!r} --type {item.get('type', 'web')!r} "
                f"--title {item.get('title', 'Untitled')!r} --url {item.get('url', '')!r} --file path/to/source.txt"
            )


if __name__ == "__main__":
    main()
