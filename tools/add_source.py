#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date

from advisor_lib import advisor_dir, append_json_records, build_context_notes, fetch_url_text, read_text


def main() -> None:
    parser = argparse.ArgumentParser(description="Add a manual or URL source to an advisor folder.")
    parser.add_argument("advisor")
    parser.add_argument("--type", default="note", choices=["note", "blog", "publication", "linkedin", "social", "youtube", "web"])
    parser.add_argument("--title", required=True)
    parser.add_argument("--url", default="")
    parser.add_argument("--date", default="")
    parser.add_argument("--file", help="Local text/markdown file to ingest.")
    parser.add_argument("--fetch-url", action="store_true", help="Fetch and clean URL text with urllib.")
    parser.add_argument("--text", default="", help="Short text to store directly.")
    args = parser.parse_args()

    text = args.text
    if args.file:
        text = read_text(advisor_dir(args.advisor) / args.file if not args.file.startswith("/") else __import__("pathlib").Path(args.file))
    elif args.fetch_url and args.url:
        text = fetch_url_text(args.url)

    record = {
        "title": args.title,
        "type": args.type,
        "url": args.url,
        "date": args.date,
        "captured_date": date.today().isoformat(),
        "text": text.strip(),
    }
    output = advisor_dir(args.advisor) / "sources.json"
    append_json_records(output, [record])
    notes = build_context_notes(args.advisor)
    print(f"Added source to {output}: {args.title}")
    print(f"Updated {notes}")


if __name__ == "__main__":
    main()
