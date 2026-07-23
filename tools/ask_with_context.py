#!/usr/bin/env python3
from __future__ import annotations

import argparse
from io import StringIO

from advisor_lib import format_source_note, infer_use_case, iter_advisor_chunks, rank_chunks


def bullet_from_text(text: str, max_len: int = 340) -> str:
    text = " ".join(text.split())
    if len(text) <= max_len:
        return text
    cut = text[:max_len].rsplit(" ", 1)[0]
    return cut + "..."


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a non-LLM, source-grounded draft from retrieved advisor context.")
    parser.add_argument("advisor")
    parser.add_argument("question")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--prefer-recent-years", type=int)
    parser.add_argument("--output", help="Optional markdown file path inside the advisor folder or absolute path.")
    args = parser.parse_args()

    chunks = iter_advisor_chunks(args.advisor)
    ranked = rank_chunks(chunks, args.question, limit=args.limit, prefer_recent_years=args.prefer_recent_years)
    use_case = infer_use_case(args.question)

    out = StringIO()
    emit = lambda text="": print(text, file=out)

    emit(f"# Draft Response: {args.advisor}\n")
    emit(f"Question: {args.question}\n")
    emit(f"Detected use case: {use_case}\n")
    emit("## Short Answer\n")
    if ranked:
        emit(
            "Based on the saved local context, the strongest relevant themes are below. "
            "This is an extractive draft, not a full LLM synthesis."
        )
    else:
        emit("No relevant local context was found. Add sources or broaden the query.")
        print(out.getvalue())
        return

    emit("\n## Likely Advisor Framing\n")
    for chunk in ranked[:3]:
        emit(f"- {bullet_from_text(chunk.text)}")

    emit("\n## Key Themes From Saved Context\n")
    for chunk in ranked[3:8]:
        emit(f"- {bullet_from_text(chunk.text)}")

    if use_case == "interview prep":
        emit("\n## Suggested Interview Questions\n")
        emit("- How do you distinguish vulnerability volume from actual business risk?")
        emit("- What signals tell you that continuous monitoring is working rather than just creating dashboards?")
        emit("- Where should security teams draw the line between developer-owned remediation and central governance?")
        emit("- What does good executive or board-level reporting look like when the underlying signals are technical?")
        emit("- What changed in your perspective moving from product security into broader assurance or risk leadership?")

    emit("\n## Source Notes\n")
    for chunk in ranked[: args.limit]:
        emit(f"- {format_source_note(chunk)}")

    text = out.getvalue()
    if args.output:
        from pathlib import Path

        from advisor_lib import advisor_dir, write_text

        output = Path(args.output)
        if not output.is_absolute():
            output = advisor_dir(args.advisor) / output
        write_text(output, text)
        print(f"Wrote {output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
