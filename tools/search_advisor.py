#!/usr/bin/env python3
from __future__ import annotations

import argparse

from advisor_lib import format_source_note, iter_advisor_chunks, rank_chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="Search a selected advisor's local context.")
    parser.add_argument("advisor")
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--prefer-recent-years", type=int)
    args = parser.parse_args()

    chunks = iter_advisor_chunks(args.advisor)
    ranked = rank_chunks(chunks, args.query, limit=args.limit, prefer_recent_years=args.prefer_recent_years)
    for idx, chunk in enumerate(ranked, 1):
        print(f"\n## {idx}. score={chunk.score:.2f}")
        print(format_source_note(chunk))
        print(chunk.text[:900].strip())


if __name__ == "__main__":
    main()

