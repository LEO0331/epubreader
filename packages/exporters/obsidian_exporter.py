from __future__ import annotations

import re
import shutil
from datetime import UTC, datetime
from pathlib import Path

_MARKDOWN_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_HTML_IMAGE_RE = re.compile(r"<img\s+[^>]*src=[\"']([^\"']+)[\"'][^>]*>", re.IGNORECASE)


def export_obsidian(
    *,
    output_dir: Path,
    collection_name: str,
    books: list[dict[str, object]],
    profile: str = "basic",
) -> Path:
    if profile == "basic":
        return _export_obsidian_basic(
            output_dir=output_dir,
            collection_name=collection_name,
            books=books,
        )
    if profile == "enhanced":
        return _export_obsidian_enhanced(
            output_dir=output_dir,
            collection_name=collection_name,
            books=books,
        )
    raise ValueError(f"Unsupported obsidian export profile: {profile}")


def _export_obsidian_basic(
    *,
    output_dir: Path,
    collection_name: str,
    books: list[dict[str, object]],
) -> Path:
    target = output_dir / "obsidian" / _slug(collection_name)
    target.mkdir(parents=True, exist_ok=True)

    index_lines = [f"# {collection_name}", ""]
    for book in sorted(books, key=lambda b: str(b.get("id", ""))):
        book_id = str(book["id"])
        note_name = f"{book_id}.md"
        index_lines.append(f"- [[{book_id}]]")

        note = [
            f"# {book_id}",
            "",
            "## Summary",
            str(book.get("summary", "")),
            "",
            "## Wiki",
            str(book.get("wiki", "")),
        ]
        (target / note_name).write_text("\n".join(note), encoding="utf-8")

    (target / "index.md").write_text("\n".join(index_lines), encoding="utf-8")
    return target


def _export_obsidian_enhanced(
    *,
    output_dir: Path,
    collection_name: str,
    books: list[dict[str, object]],
) -> Path:
    collection_slug = _slug(collection_name)
    target = output_dir / "obsidian" / collection_slug
    target.mkdir(parents=True, exist_ok=True)

    index_lines = [f"# {collection_name}", ""]
    for book in sorted(books, key=lambda b: str(b.get("id", ""))):
        book_id = str(book["id"])
        note_name = f"{book_id}.md"
        index_lines.append(f"- [[{book_id}]]")

        warning_messages: list[str] = []
        summary_text = str(book.get("summary", ""))
        wiki_text = str(book.get("wiki", ""))
        source_type = str(book.get("source_type", "unknown"))

        context_roots = _context_roots_for_book(book=book)

        summary_text = _rewrite_embedded_images(
            text=summary_text,
            target=target,
            book_id=book_id,
            context_roots=context_roots,
            warning_messages=warning_messages,
        )
        wiki_text = _rewrite_embedded_images(
            text=wiki_text,
            target=target,
            book_id=book_id,
            context_roots=context_roots,
            warning_messages=warning_messages,
        )

        frontmatter_lines = _build_frontmatter(
            collection_name=collection_name,
            collection_slug=collection_slug,
            book=book,
            source_type=source_type,
            warning_messages=warning_messages,
        )

        note = [
            *frontmatter_lines,
            f"# {book_id}",
            "",
            "## Summary",
            summary_text,
            "",
            "## Wiki",
            wiki_text,
        ]
        (target / note_name).write_text("\n".join(note), encoding="utf-8")

    (target / "index.md").write_text("\n".join(index_lines), encoding="utf-8")
    return target


def _slug(value: str) -> str:
    clean = "".join(ch.lower() if ch.isalnum() else "_" for ch in value)
    while "__" in clean:
        clean = clean.replace("__", "_")
    return clean.strip("_") or "collection"


def _context_roots_for_book(*, book: dict[str, object]) -> list[Path]:
    roots: list[Path] = []
    for key in ("summary_path", "wiki_path"):
        raw = book.get(key)
        if isinstance(raw, str) and raw:
            roots.append(Path(raw).resolve().parent)
    return roots


def _build_frontmatter(
    *,
    collection_name: str,
    collection_slug: str,
    book: dict[str, object],
    source_type: str,
    warning_messages: list[str],
) -> list[str]:
    book_id = str(book.get("id", ""))
    title = str(book.get("title", "")).strip() or book_id

    tags = [
        "book-qa-library",
        f"source/{_slug(source_type)}",
        f"collection/{collection_slug}",
    ]
    created_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    lines = [
        "---",
        f'title: "{_yaml_escape(title)}"',
        f'book_id: "{_yaml_escape(book_id)}"',
        f'source_type: "{_yaml_escape(source_type)}"',
        f'collection: "{_yaml_escape(collection_name)}"',
        "tags:",
    ]
    for tag in tags:
        lines.append(f'  - "{_yaml_escape(tag)}"')
    lines.append(f'created_at: "{created_at}"')
    if title != book_id:
        lines.extend(
            [
                "aliases:",
                f'  - "{_yaml_escape(title)}"',
            ]
        )
    if warning_messages:
        lines.append("export_warnings:")
        for warning in warning_messages:
            lines.append(f'  - "{_yaml_escape(warning)}"')
    lines.extend(["---", ""])
    return lines


def _rewrite_embedded_images(
    *,
    text: str,
    target: Path,
    book_id: str,
    context_roots: list[Path],
    warning_messages: list[str],
) -> str:
    rewritten = _MARKDOWN_IMAGE_RE.sub(
        lambda match: _replace_markdown_image(
            match=match,
            target=target,
            book_id=book_id,
            context_roots=context_roots,
            warning_messages=warning_messages,
        ),
        text,
    )
    rewritten = _HTML_IMAGE_RE.sub(
        lambda match: _replace_html_image(
            match=match,
            target=target,
            book_id=book_id,
            context_roots=context_roots,
            warning_messages=warning_messages,
        ),
        rewritten,
    )
    return rewritten


def _replace_markdown_image(
    *,
    match: re.Match[str],
    target: Path,
    book_id: str,
    context_roots: list[Path],
    warning_messages: list[str],
) -> str:
    alt = match.group(1)
    source = match.group(2).strip()
    rewritten = _resolve_and_copy_local_asset(
        source=source,
        target=target,
        book_id=book_id,
        context_roots=context_roots,
        warning_messages=warning_messages,
    )
    return f"![{alt}]({rewritten})"


def _replace_html_image(
    *,
    match: re.Match[str],
    target: Path,
    book_id: str,
    context_roots: list[Path],
    warning_messages: list[str],
) -> str:
    source = match.group(1).strip()
    rewritten = _resolve_and_copy_local_asset(
        source=source,
        target=target,
        book_id=book_id,
        context_roots=context_roots,
        warning_messages=warning_messages,
    )
    return match.group(0).replace(source, rewritten, 1)


def _resolve_and_copy_local_asset(
    *,
    source: str,
    target: Path,
    book_id: str,
    context_roots: list[Path],
    warning_messages: list[str],
) -> str:
    source_clean = source.strip()
    lower = source_clean.lower()
    if lower.startswith(("http://", "https://", "data:")):
        return source_clean

    candidate_path = _find_local_asset_candidate(
        source=source_clean,
        context_roots=context_roots,
    )
    if candidate_path is None:
        warning_messages.append(f"Unresolved local image asset: {source_clean}")
        return source_clean

    assets_dir = target / "assets" / book_id
    assets_dir.mkdir(parents=True, exist_ok=True)
    safe_name = candidate_path.name
    out_path = assets_dir / safe_name
    shutil.copy2(candidate_path, out_path)
    return (Path("assets") / book_id / safe_name).as_posix()


def _find_local_asset_candidate(*, source: str, context_roots: list[Path]) -> Path | None:
    if not context_roots:
        return None
    source_path = Path(source)
    for root in context_roots:
        candidate = (root / source_path).resolve()
        if not _is_within_root(candidate, root):
            continue
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def _is_within_root(candidate: Path, root: Path) -> bool:
    if candidate == root:
        return True
    return root in candidate.parents


def _yaml_escape(value: str) -> str:
    sanitized = (
        value.replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("\n", " ")
        .replace("\t", " ")
    )
    return sanitized.replace("\\", "\\\\").replace('"', '\\"')
