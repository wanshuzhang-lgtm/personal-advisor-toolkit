#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from advisor_lib import advisor_dir, build_context_notes, load_json, raw_vtt_dir, write_json


TIMING_RE = re.compile(
    r"(?P<start>\d\d:\d\d:\d\d\.\d{3})\s+-->\s+(?P<end>\d\d:\d\d:\d\d\.\d{3})(?:\s+.*)?"
)


def clean_caption(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&amp;", "&")
    return " ".join(text.split())


def collapse_repeated_segments(segments: list[dict[str, str]]) -> str:
    lines: list[str] = []
    previous = ""
    for segment in segments:
        text = segment["text"].strip()
        if not text or text == previous:
            continue
        if previous and text.startswith(previous):
            text = text[len(previous) :].strip()
        if text:
            lines.append(text)
            previous = segment["text"].strip()
    return " ".join(lines)


def parse_vtt(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    segments: list[dict[str, str]] = []
    idx = 0
    while idx < len(lines):
        match = TIMING_RE.match(lines[idx].strip())
        if not match:
            idx += 1
            continue
        start, end = match.group("start"), match.group("end")
        idx += 1
        payload: list[str] = []
        while idx < len(lines) and lines[idx].strip():
            payload.append(lines[idx])
            idx += 1
        text = clean_caption(" ".join(payload))
        if text:
            segments.append({"start": start, "end": end, "text": text})
        idx += 1

    video_id = ""
    id_match = re.search(r"\[([A-Za-z0-9_-]{8,})\]", path.name)
    if id_match:
        video_id = id_match.group(1)
    title = re.sub(r"\s*\[[A-Za-z0-9_-]{8,}\].*$", "", path.stem)
    title = re.sub(r"\.en$", "", title)
    record = {
        "title": title,
        "type": "youtube",
        "youtube_id": video_id,
        "youtube_url": f"https://www.youtube.com/watch?v={video_id}" if video_id else "",
        "source_file": str(path),
        "transcript_context": collapse_repeated_segments(segments),
        "segments": segments,
    }
    return record


def record_key(record: dict[str, object]) -> str:
    youtube_id = str(record.get("youtube_id") or "")
    if youtube_id:
        return f"youtube:{youtube_id}"
    source_file = str(record.get("source_file") or "")
    return f"file:{Path(source_file).name}" if source_file else str(record.get("title") or "")


def merge_records(existing: list[dict[str, object]], parsed: list[dict[str, object]]) -> list[dict[str, object]]:
    by_key = {record_key(record): record for record in existing if record_key(record)}
    ordered = list(existing)
    for record in parsed:
        key = record_key(record)
        if key in by_key:
            existing_record = by_key[key]
            if record.get("source_file"):
                existing_record["source_file"] = record["source_file"]
            continue
        ordered.append(record)
        by_key[key] = record
    return ordered


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert advisor raw_vtts/*.vtt captions to transcripts_clean.json.")
    parser.add_argument("advisor")
    parser.add_argument("--output", default="transcripts_clean.json")
    parser.add_argument("--vtt-dir", default="", help="Optional folder containing .vtt files. Defaults to Advisor/raw_vtts.")
    parser.add_argument("--rebuild", action="store_true", help="Replace output with parsed VTT records instead of merging with existing JSON.")
    args = parser.parse_args()

    folder = advisor_dir(args.advisor)
    input_folder = Path(args.vtt_dir) if args.vtt_dir else raw_vtt_dir(args.advisor)
    records = [parse_vtt(path) for path in sorted(input_folder.glob("*.vtt"))]
    output = folder / args.output
    if output.exists() and not args.rebuild:
        loaded = load_json(output)
        existing = loaded if isinstance(loaded, list) else []
        records = merge_records(existing, records)
    write_json(output, records)
    notes = build_context_notes(args.advisor)
    print(f"Wrote {len(records)} transcript records to {output}")
    print(f"Updated {notes}")


if __name__ == "__main__":
    main()
