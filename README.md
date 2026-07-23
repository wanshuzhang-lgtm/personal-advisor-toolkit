# Personal Advisor

Local, folder-based toolkit for building "expert context" packs from a selected person's saved material.

The MVP does not require an LLM API, SDK, local model, database, or app server. It prepares and searches context so you can ask Codex, Claude Code, Cursor, or ChatGPT to reason over the files directly.

## Folder Model

One advisor per folder:

```text
Personal Advisor/
  Alex Kreilein/
    raw_vtts/
    transcripts_clean.json
    context_notes.md
    sources_todo.md
    context_pack.md
  Andrej Karpathy/
    sources_todo.md
    sources.json
    context_pack.md
  tools/
```

Each advisor folder can contain:

- `.json`: transcript/source records
- `.md`: generated context notes, source lists, context packs
- `.txt`: raw notes or transcripts
- `raw_vtts/*.vtt`: raw YouTube caption files

## Core Workflow

1. Discover candidate sources:

```bash
python3 tools/discover_sources.py "Alex Kreilein" --focus "product security continuous monitoring risk controls compliance"
```

2. Review `Advisor Name/sources_todo.md` and check the sources to ingest by changing `[ ]` to `[x]`.

3. Optionally discover YouTube candidates with metadata:

```bash
python3 tools/discover_youtube.py "Alex Kreilein" --focus "product security continuous monitoring risk controls compliance" --limit 8
```

This appends candidate videos to `sources_todo.md` with title, URL, date, channel, duration, description, and a review note.

4. Ingest selected sources. Add `--execute-youtube` to download checked YouTube captions into `raw_vtts/` and rebuild `transcripts_clean.json`:

```bash
python3 tools/ingest_selected_sources.py "Alex Kreilein" --execute-youtube
```

5. Search an advisor folder:

```bash
python3 tools/search_advisor.py "Alex Kreilein" "continuous monitoring risk controls compliance"
```

6. Build a context pack:

```bash
python3 tools/build_context_pack.py "Alex Kreilein" "interview prep continuous monitoring risk controls compliance"
```

For repeated questions where you want history instead of overwriting `context_pack.md`:

```bash
python3 tools/build_context_pack.py "Alex Kreilein" "question here" --save-run
```

7. Ask in Codex, Claude Code, Cursor, or ChatGPT:

```text
Read Alex Kreilein/context_pack.md.
I need to meet Alex for a 30 minute interview. Help me understand his perspective on continuous monitoring, working style, compliance, security signals, risk, and controls.
```

## Optional YouTube Ingestion

If `yt-dlp` is installed:

```bash
python3 tools/add_youtube.py "Alex Kreilein" "https://www.youtube.com/watch?v=CHn0Bs8Ep78"
```

`add_youtube.py` skips videos already present in `transcripts_clean.json`.

If you already have `.vtt` files in the advisor `raw_vtts/` folder:

```bash
python3 tools/vtt_to_json.py "Alex Kreilein"
```

By default, this merges new VTT records into `transcripts_clean.json` and preserves existing records. Use `--rebuild` only when you intentionally want to recreate the transcript JSON from all raw VTT files.

## Text Source Ingestion

For checked blogs, articles, publications, and public pages, `ingest_selected_sources.py` tries to fetch and save text automatically by default. If fetching fails, returns no useful text, or the source is login-gated, it saves metadata and prints a clear manual action message.

Manual copy/paste is mainly for LinkedIn, private pages, paywalled pages, or blocked pages:

```bash
python3 tools/add_source.py "Alex Kreilein" --type linkedin --title "Post title" --url "https://..." --file post.txt
```

LinkedIn is manual-fallback-first because automated LinkedIn scraping is brittle and can create account/platform issues. The tool should tell you when manual text is needed and what command to run.

Text sources are deduped before writing to `sources.json`. The dedupe key prefers `source_id`, then YouTube ID, then a canonicalized URL with common tracking parameters removed. If there is no URL, it falls back to source type plus title.

## Non-LLM Ask Helper

This script does not call a model. It produces a structured, source-grounded draft from retrieved snippets:

```bash
python3 tools/ask_with_context.py "Alex Kreilein" "I need to meet Alex for a 30 min interview..."
```

Use it as a quick baseline. For better synthesis, point an LLM coding assistant at the generated `context_pack.md`.

## Context Notes

Each advisor should have:

```text
Advisor/context_notes.md
```

This is a generated short inventory of what is already saved in `sources.json` and `transcripts_clean.json`. It includes title, source type, publication/capture date, URL, storage file, capture status, and a short description.

It is updated automatically after:

- `tools/add_source.py`
- `tools/ingest_selected_sources.py`
- `tools/vtt_to_json.py`

You can regenerate it manually:

```bash
python3 tools/build_context_notes.py "Advisor Name"
```
