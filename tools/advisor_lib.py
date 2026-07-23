from __future__ import annotations

import html
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote_plus, urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR_NAME = "_generated"
RUNS_DIR_NAME = "_runs"
SKIP_FILENAMES = {"context_pack.md", "sources_todo.md", "transcripts.txt", "context_notes.md"}
RAW_VTT_DIR_NAME = "raw_vtts"


@dataclass
class SourceChunk:
    advisor: str
    source_file: str
    title: str
    source_type: str
    url: str
    date: str
    text: str
    score: float = 0.0


def advisor_dir(name: str) -> Path:
    path = ROOT / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def raw_vtt_dir(name: str) -> Path:
    path = advisor_dir(name) / RAW_VTT_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def slugify(value: str, max_len: int = 80) -> str:
    value = re.sub(r"[^A-Za-z0-9._ -]+", "", value).strip().replace(" ", "_")
    value = re.sub(r"_+", "_", value)
    return value[:max_len] or "source"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(read_text(path))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def canonical_url(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    parsed = urlparse(value)
    if not parsed.scheme or not parsed.netloc:
        return value.rstrip("/")
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    query = parse_qs(parsed.query, keep_blank_values=True)
    query = {
        key: vals
        for key, vals in query.items()
        if not key.lower().startswith("utm_") and key.lower() not in {"fbclid", "gclid", "mc_cid", "mc_eid"}
    }
    query_string = urlencode(query, doseq=True)
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((scheme, netloc, path, "", query_string, ""))


def source_key(record: dict[str, Any]) -> str:
    explicit = str(record.get("source_id") or "").strip()
    if explicit:
        return explicit
    youtube_id_value = str(record.get("youtube_id") or "").strip()
    if youtube_id_value:
        return f"youtube:{youtube_id_value}"
    url = canonical_url(str(record.get("url") or record.get("youtube_url") or ""))
    if url:
        return f"url:{url}"
    title = slugify(str(record.get("title") or "").lower())
    source_type = str(record.get("type") or "source").lower()
    return f"{source_type}:{title}" if title else ""


def append_json_records(path: Path, records: list[dict[str, Any]]) -> None:
    existing: list[dict[str, Any]] = []
    if path.exists():
        loaded = load_json(path)
        if isinstance(loaded, list):
            existing = loaded
    for item in existing:
        if isinstance(item, dict) and not item.get("source_id"):
            key = source_key(item)
            if key:
                item["source_id"] = key
            if item.get("url"):
                item["canonical_url"] = canonical_url(str(item["url"]))
    seen = {source_key(item) for item in existing if isinstance(item, dict)}
    by_key = {source_key(item): item for item in existing if isinstance(item, dict)}
    for record in records:
        key = source_key(record)
        if key and key in by_key:
            existing_record = by_key[key]
            new_text = str(record.get("text") or "").strip()
            old_text = str(existing_record.get("text") or "").strip()
            if new_text and not old_text:
                existing_record.update(record)
                existing_record["source_id"] = key
                if existing_record.get("url"):
                    existing_record["canonical_url"] = canonical_url(str(existing_record["url"]))
            continue
        if key and key not in seen:
            record["source_id"] = key
            if record.get("url"):
                record["canonical_url"] = canonical_url(str(record["url"]))
            existing.append(record)
            seen.add(key)
    write_json(path, existing)


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9][a-z0-9.+#-]*", text.lower())


def split_chunks(text: str, max_words: int = 260, overlap: int = 40) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    step = max(1, max_words - overlap)
    for start in range(0, len(words), step):
        part = words[start : start + max_words]
        if part:
            chunks.append(" ".join(part))
        if start + max_words >= len(words):
            break
    return chunks


def extract_record_text(record: dict[str, Any]) -> str:
    for key in ("transcript_context", "text", "content", "summary", "notes"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    segments = record.get("segments")
    if isinstance(segments, list):
        return " ".join(str(item.get("text", "")) for item in segments if isinstance(item, dict)).strip()
    return ""


def iter_advisor_chunks(advisor: str, max_words: int = 260) -> list[SourceChunk]:
    folder = advisor_dir(advisor)
    chunks: list[SourceChunk] = []
    for path in sorted(folder.rglob("*")):
        if GENERATED_DIR_NAME in path.parts or RUNS_DIR_NAME in path.parts or not path.is_file():
            continue
        if (
            path.name.startswith(".")
            or path.name in SKIP_FILENAMES
            or path.name.startswith("answer_")
            or path.suffix.lower() in {".vtt", ".ds_store"}
        ):
            continue
        rel = str(path.relative_to(folder))
        suffix = path.suffix.lower()
        if suffix == ".json":
            try:
                data = load_json(path)
            except Exception:
                continue
            records = data if isinstance(data, list) else [data]
            for record in records:
                if not isinstance(record, dict):
                    continue
                text = extract_record_text(record)
                if not text:
                    continue
                title = str(record.get("title") or path.stem)
                url = str(record.get("url") or record.get("youtube_url") or "")
                source_type = str(record.get("type") or ("youtube" if record.get("youtube_url") else "json"))
                source_date = str(record.get("date") or record.get("published_date") or "")
                for part in split_chunks(text, max_words=max_words):
                    chunks.append(SourceChunk(advisor, rel, title, source_type, url, source_date, part))
        elif suffix in {".md", ".txt"}:
            text = read_text(path).strip()
            if not text:
                continue
            for part in split_chunks(text, max_words=max_words):
                chunks.append(SourceChunk(advisor, rel, path.stem, suffix.lstrip("."), "", "", part))
    return chunks


def parse_year(value: str) -> int | None:
    match = re.search(r"(20\d{2}|19\d{2})", value or "")
    return int(match.group(1)) if match else None


def rank_chunks(
    chunks: list[SourceChunk],
    query: str,
    limit: int = 12,
    prefer_recent_years: int | None = None,
) -> list[SourceChunk]:
    query_terms = Counter(tokenize(query))
    if not query_terms:
        return chunks[:limit]
    docs = [Counter(tokenize(chunk.text + " " + chunk.title)) for chunk in chunks]
    df = Counter()
    for doc in docs:
        for term in doc:
            df[term] += 1
    current_year = date.today().year
    ranked: list[SourceChunk] = []
    for chunk, doc in zip(chunks, docs):
        score = 0.0
        for term, q_count in query_terms.items():
            if term not in doc:
                continue
            idf = math.log((1 + len(docs)) / (1 + df[term])) + 1
            score += q_count * doc[term] * idf
        for term in query_terms:
            if term in chunk.title.lower():
                score += 2.0
        if prefer_recent_years:
            year = parse_year(chunk.date) or parse_year(chunk.title) or parse_year(chunk.source_file)
            if year:
                age = max(0, current_year - year)
                if age <= prefer_recent_years:
                    score *= 1.25
                elif age > prefer_recent_years + 4:
                    score *= 0.85
        if score > 0:
            ranked.append(SourceChunk(**{**chunk.__dict__, "score": score}))
    ranked.sort(key=lambda item: item.score, reverse=True)
    return ranked[:limit]


def fetch_url_text(url: str, timeout: int = 20) -> str:
    req = Request(url, headers={"User-Agent": "PersonalAdvisor/0.1"})
    with urlopen(req, timeout=timeout) as response:
        raw = response.read().decode("utf-8", errors="ignore")
    raw = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", raw)
    raw = re.sub(r"(?is)<br\s*/?>", "\n", raw)
    raw = re.sub(r"(?is)</p\s*>", "\n\n", raw)
    raw = re.sub(r"(?is)<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    raw = re.sub(r"[ \t]+", " ", raw)
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw.strip()


def youtube_id(url: str) -> str:
    parsed = urlparse(url)
    if parsed.hostname and "youtu.be" in parsed.hostname:
        return parsed.path.strip("/")
    query = parse_qs(parsed.query)
    if "v" in query:
        return query["v"][0]
    return ""


def search_url(query: str) -> str:
    return "https://duckduckgo.com/?q=" + quote_plus(query)


def infer_use_case(question: str) -> str:
    q = question.lower()
    if any(term in q for term in ("interview", "meet with", "prep", "30 min", "30-minute")):
        return "interview prep"
    if any(term in q for term in ("compare", "versus", " vs ")):
        return "comparison"
    if any(term in q for term in ("understand", "explain", "learn")):
        return "explanation / learning"
    if any(term in q for term in ("should i", "decision", "recommend")):
        return "decision support"
    return "perspective extraction"


def format_source_note(chunk: SourceChunk) -> str:
    label = chunk.title
    if chunk.date:
        label += f" ({chunk.date})"
    if chunk.url:
        label += f" - {chunk.url}"
    return f"{label} [{chunk.source_file}]"


def source_excerpt(text: str, max_len: int = 280) -> str:
    text = " ".join((text or "").split())
    if len(text) <= max_len:
        return text
    return text[:max_len].rsplit(" ", 1)[0] + "..."


def source_date(record: dict[str, Any]) -> str:
    return str(
        record.get("published_date")
        or record.get("date")
        or record.get("upload_date")
        or record.get("captured_date")
        or ""
    )


def build_context_notes(advisor: str) -> Path:
    folder = advisor_dir(advisor)
    rows: list[dict[str, str]] = []
    for filename, default_type in (("transcripts_clean.json", "youtube"), ("sources.json", "source")):
        path = folder / filename
        if not path.exists():
            continue
        try:
            loaded = load_json(path)
        except Exception:
            continue
        records = loaded if isinstance(loaded, list) else []
        for record in records:
            if not isinstance(record, dict):
                continue
            text = extract_record_text(record)
            title = str(record.get("title") or "Untitled")
            source_type = str(record.get("type") or default_type)
            url = str(record.get("youtube_url") or record.get("url") or "")
            rows.append(
                {
                    "title": title,
                    "type": source_type,
                    "date": source_date(record),
                    "url": url,
                    "file": filename,
                    "status": str(record.get("capture_status") or ("text_saved" if text else "metadata_only")),
                    "description": source_excerpt(str(record.get("why_relevant") or record.get("description") or text)),
                }
            )

    rows.sort(key=lambda item: item["date"] or "0000-00-00", reverse=True)
    lines = [
        f"# Context Notes: {advisor}",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "This file is a generated source inventory. It summarizes what is already saved in `sources.json` and `transcripts_clean.json` so a user can quickly understand available context and source recency.",
        "",
        "## Saved Sources",
        "",
    ]
    if not rows:
        lines.append("No saved sources yet.")
    for idx, row in enumerate(rows, 1):
        lines.extend(
            [
                f"### {idx}. {row['title']}",
                "",
                f"- Type: {row['type']}",
                f"- Date: {row['date'] or 'unknown'}",
                f"- Status: {row['status']}",
                f"- Stored in: {row['file']}",
                f"- URL: {row['url'] or 'n/a'}",
                f"- Short description: {row['description'] or 'No description available.'}",
                "",
            ]
        )
    output = folder / "context_notes.md"
    write_text(output, "\n".join(lines))
    return output
