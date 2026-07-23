#!/usr/bin/env python3
from __future__ import annotations

import argparse

from advisor_lib import build_context_notes


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Advisor/context_notes.md from saved sources and transcripts.")
    parser.add_argument("advisor")
    args = parser.parse_args()

    output = build_context_notes(args.advisor)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
