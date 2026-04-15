from __future__ import annotations

from enum import StrEnum


class SourceType(StrEnum):
    EPUB_URL = "epub_url"
    UPLOADED_EPUB = "uploaded_epub"
    MIZ_BOOKS = "miz_books"
    PLAIN_TEXT = "plain_text"


class BookStatus(StrEnum):
    INGESTED = "ingested"
    PARSED = "parsed"
    CLEANED = "cleaned"
    CHUNKED = "chunked"
    INDEXED = "indexed"
    FAILED = "failed"


class JobType(StrEnum):
    INGEST = "ingest"
    PARSE = "parse"
    CLEAN = "clean"
    CHUNK = "chunk"
    ARTIFACT = "artifact"
    INDEX = "index"
    QUERY = "query"


class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
    COMPLETED = "completed"


class ArtifactType(StrEnum):
    SOURCE_MANIFEST = "source_manifest"
    PARSED = "parsed"
    CLEANED = "cleaned"
    CHUNKS = "chunks"
    SUMMARY = "summary"
    WIKI = "wiki"
    SKILL = "skill"
    QA = "qa"


class CollectionType(StrEnum):
    USER = "user"
    SYSTEM = "system"
