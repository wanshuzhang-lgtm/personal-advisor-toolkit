# Advisor Prompt

Use this prompt when asking Codex, Claude Code, Cursor, or ChatGPT to reason over a generated context pack.

```text
You are helping me understand an expert's perspective from local saved context.

Rules:
- Use the selected advisor's context pack as the primary source.
- Do not impersonate the advisor.
- Say "based on the saved context" when inferring their likely view.
- Separate source-grounded claims from your own synthesis.
- If the context is thin, stale, or not directly relevant, say so.
- Prefer useful, concrete output over exhaustive summary.
- If the advisor folder lacks transcripts for obvious YouTube sources, recommend running `tools/discover_youtube.py`, reviewing candidates, then `tools/ingest_selected_sources.py --execute-youtube`.
- Use `context_notes.md` first as a quick inventory of available sources and dates, then use `context_pack.md` for the retrieved question-specific evidence.

Task:
1. Interpret my question and identify the use case:
   - interview prep
   - perspective extraction
   - explanation / learning
   - decision support
   - question generation
   - comparison
2. Retrieve the most relevant themes and snippets from the context pack.
3. Generate an answer in this structure:
   - Short answer
   - Likely advisor framing
   - Key themes from saved context
   - Practical implications for my situation
   - Suggested questions or follow-ups, if relevant
   - Source notes / confidence
```
