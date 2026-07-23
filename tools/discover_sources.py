#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date

from advisor_lib import advisor_dir, search_url, write_text


def candidate_queries(advisor: str, focus: str) -> list[tuple[str, str]]:
    base = [
        f'"{advisor}" {focus}',
        f'"{advisor}" interview {focus}',
        f'"{advisor}" blog {focus}',
        f'"{advisor}" podcast {focus}',
        f'site:youtube.com "{advisor}" {focus}',
        f'site:linkedin.com/in "{advisor}"',
        f'site:linkedin.com/posts "{advisor}" {focus}',
    ]
    return [(query, search_url(query)) for query in base]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a reviewable source discovery checklist.")
    parser.add_argument("advisor")
    parser.add_argument("--focus", default="")
    parser.add_argument("--url", action="append", default=[], help="Seed URL to include as a candidate. Format type|title|url|why")
    args = parser.parse_args()

    folder = advisor_dir(args.advisor)
    lines = [
        f"# Source Discovery: {args.advisor}",
        "",
        f"Generated: {date.today().isoformat()}",
        f"Focus: {args.focus or '(general)'}",
        "",
        "## Search Queries",
        "",
    ]
    for query, url in candidate_queries(args.advisor, args.focus):
        lines.extend(
            [
                f"- [ ] Search: {query}",
                "  Type: search",
                f"  URL: {url}",
                "  Date:",
                "  Why relevant: Candidate discovery query.",
                "",
            ]
        )

    if args.url:
        lines.extend(["## Seed Candidates", ""])
        for raw in args.url:
            parts = [part.strip() for part in raw.split("|", 3)]
            while len(parts) < 4:
                parts.append("")
            source_type, title, url, why = parts
            lines.extend(
                [
                    f"- [ ] {title or url}",
                    f"  Type: {source_type or 'web'}",
                    f"  URL: {url}",
                    "  Date:",
                    f"  Why relevant: {why or 'Seeded by user or assistant.'}",
                    "",
                ]
            )

    lines.extend(
        [
            "## Notes",
            "",
            "- Change `[ ]` to `[x]` for sources you want to ingest.",
            "- LinkedIn sources are metadata-first; copy/paste post text with `tools/add_source.py`.",
            "- Search rows are prompts for manual or assistant-assisted discovery, not ingestible source content.",
            "",
        ]
    )

    output = folder / "sources_todo.md"
    write_text(output, "\n".join(lines))
    print(f"Wrote discovery checklist to {output}")


if __name__ == "__main__":
    main()

