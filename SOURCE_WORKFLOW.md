# Source Workflow

The product should stay reviewable. Discovery creates a checklist; ingestion acts only on reviewed items.

## Source Types

- `youtube`: videos with captions/transcripts
- `blog`: first-party or third-party articles
- `publication`: papers, formal publications, talks, PDFs
- `linkedin`: LinkedIn posts or profile pages
- `social`: X/Twitter, newsletters, podcasts, interviews
- `note`: manually written context

## Discovery

Discovery should answer: "What should I consider collecting?"

The output is `sources_todo.md` inside the advisor folder.

Each candidate looks like:

```md
- [ ] Title
  Type: youtube
  URL: https://www.youtube.com/watch?v=...
  Date:
  Why relevant: Product security and continuous monitoring.
```

Check items with `[x]` before ingestion.

For YouTube-specific discovery, use:

```bash
python3 tools/discover_youtube.py "Advisor Name" --focus "topic words" --limit 8
```

This uses `yt-dlp` search metadata only. It does not download transcripts yet. It appends candidate videos with title, URL, date, channel, duration, description, and a "why relevant" note.

## Ingestion

Ingestion should answer: "What has the user approved to save locally?"

- YouTube: download captions with `yt-dlp` into `Advisor/raw_vtts/`, then merge `.vtt` records into `transcripts_clean.json`.
- Blog/article/public page: auto-fetch and clean text by default; if blocked or empty, save metadata and print manual copy/paste instructions.
- LinkedIn: save URL/metadata and print manual copy/paste instructions when text is needed.
- PDF: save URL/metadata first; add extraction later if needed.
- Context inventory: after ingestion, generate `Advisor/context_notes.md` from `sources.json` and `transcripts_clean.json`.

Text-format sources are deduped before writing to `sources.json`. The dedupe key is:

```text
source_id -> youtube_id -> canonical URL -> type:title
```

Canonical URLs remove common tracking parameters and normalize `www` and trailing slashes.

## Context Notes

`context_notes.md` is a generated source inventory for each advisor. It is meant for quick inspection, not retrieval. It should summarize:

- title
- source type
- publication/upload/capture date
- URL
- whether full text was saved or only metadata
- which file stores the context
- short description or excerpt

Regenerate it with:

```bash
python3 tools/build_context_notes.py "Advisor"
```

## Recency

For fast MVP work, set a recency preference in the query rather than enforcing it globally:

```bash
python3 tools/build_context_pack.py "Advisor" "question" --prefer-recent-years 3
```

Recent context should be weighted higher, but older canonical sources should not be hidden automatically.

## Repeated Questions

Default behavior:

- `context_pack.md` is the latest generated context pack and can be overwritten.
- `answer_*.md` and `context_pack.md` are generated artifacts and ignored by git.

For question history:

```bash
python3 tools/build_context_pack.py "Advisor" "question" --save-run
```

This writes to:

```text
Advisor/_runs/YYYYMMDD_HHMMSS_question_slug/context_pack.md
```

Use `_runs/` when you want to keep question-specific retrieval history. Use the default `context_pack.md` for simple latest-only work.
