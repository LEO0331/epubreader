from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.db.base import Base, TimestampMixin


class BookORM(TimestampMixin, Base):
    __tablename__ = "books"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_ref: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    raw_snapshot_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    parse_quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)


class SectionORM(Base):
    __tablename__ = "sections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    book_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("books.id"),
        nullable=False,
        index=True,
    )
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    heading: Mapped[str | None] = mapped_column(String(512), nullable=True)
    heading_path: Mapped[str] = mapped_column(Text, nullable=False, default="")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_locator: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class ChunkORM(Base):
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    book_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("books.id"),
        nullable=False,
        index=True,
    )
    section_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("sections.id"), nullable=True, index=True
    )
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class ArtifactORM(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    book_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("books.id"),
        nullable=False,
        index=True,
    )
    artifact_type: Mapped[str] = mapped_column(String(32), nullable=False)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class JobORM(TimestampMixin, Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    job_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    book_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("books.id"),
        nullable=True,
        index=True,
    )
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    current_step: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class CollectionORM(Base):
    __tablename__ = "collections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    collection_type: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class CollectionBookORM(Base):
    __tablename__ = "collection_books"

    collection_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("collections.id"),
        primary_key=True,
    )
    book_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("books.id"),
        primary_key=True,
    )


class QueryLogORM(Base):
    __tablename__ = "queries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    book_scope: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    response_preview: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
