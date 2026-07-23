#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date, datetime

from advisor_lib import advisor_dir, format_source_note, infer_use_case, iter_advisor_chunks, rank_chunks, slugify, write_text


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a compact context pack for one advisor and question.")
    parser.add_argument("advisor")
    parser.add_argument("question")
    parser.add_argument("--limit", type=int, default=14)
    parser.add_argument("--prefer-recent-years", type=int)
    parser.add_argument("--output", default="context_pack.md")
    parser.add_argument("--save-run", action="store_true", help="Write to Advisor/_runs/<timestamp>_<question_slug>/context_pack.md instead of overwriting latest.")
    args = parser.parse_args()

    chunks = iter_advisor_chunks(args.advisor)
    ranked = rank_chunks(chunks, args.question, limit=args.limit, prefer_recent_years=args.prefer_recent_years)
    use_case = infer_use_case(args.question)
    lines = [
        f"# Context Pack: {args.advisor}",
        "",
        f"Generated: {date.today().isoformat()}",
        f"Question: {args.question}",
        f"Detected use case: {use_case}",
        f"Chunks searched: {len(chunks)}",
        f"Chunks selected: {len(ranked)}",
        "",
        "## How To Use",
        "",
        "Ask an LLM assistant to use this file as the primary source. It should not impersonate the advisor; it should infer likely framing from saved context.",
        "",
        "## Answer Template",
        "",
        "- Short answer",
        "- Likely advisor framing",
        "- Key themes from saved context",
        "- Practical implications for my situation",
        "- Suggested questions or follow-ups, if relevant",
        "- Source notes / confidence",
        "",
        "## Retrieved Context",
        "",
    ]
    for idx, chunk in enumerate(ranked, 1):
        lines.extend(
            [
                f"### {idx}. {chunk.title}",
                "",
                f"Source: {format_source_note(chunk)}",
                f"Score: {chunk.score:.2f}",
                "",
                chunk.text.strip(),
                "",
            ]
        )
    if args.save_run:
        run_name = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + slugify(args.question, 48)
        output = advisor_dir(args.advisor) / "_runs" / run_name / "context_pack.md"
    else:
        output = advisor_dir(args.advisor) / args.output
    write_text(output, "\n".join(lines))
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
