"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-04-15
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "books",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=True),
        sa.Column("author", sa.String(length=255), nullable=True),
        sa.Column("language", sa.String(length=64), nullable=True),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_ref", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("raw_snapshot_path", sa.Text(), nullable=True),
        sa.Column("parse_quality_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_books")),
    )

    op.create_table(
        "sections",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("book_id", sa.String(length=36), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("heading", sa.String(length=512), nullable=True),
        sa.Column("heading_path", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_locator", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], name=op.f("fk_sections_book_id_books")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sections")),
    )
    op.create_index(op.f("ix_sections_book_id"), "sections", ["book_id"], unique=False)

    op.create_table(
        "chunks",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("book_id", sa.String(length=36), nullable=False),
        sa.Column("section_id", sa.String(length=36), nullable=True),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], name=op.f("fk_chunks_book_id_books")),
        sa.ForeignKeyConstraint(
            ["section_id"],
            ["sections.id"],
            name=op.f("fk_chunks_section_id_sections"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_chunks")),
    )
    op.create_index(op.f("ix_chunks_book_id"), "chunks", ["book_id"], unique=False)
    op.create_index(op.f("ix_chunks_section_id"), "chunks", ["section_id"], unique=False)

    op.create_table(
        "artifacts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("book_id", sa.String(length=36), nullable=False),
        sa.Column("artifact_type", sa.String(length=32), nullable=False),
        sa.Column("path", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], name=op.f("fk_artifacts_book_id_books")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_artifacts")),
    )
    op.create_index(op.f("ix_artifacts_book_id"), "artifacts", ["book_id"], unique=False)

    op.create_table(
        "jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("job_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("book_id", sa.String(length=36), nullable=True),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("current_step", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], name=op.f("fk_jobs_book_id_books")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_jobs")),
    )
    op.create_index(op.f("ix_jobs_book_id"), "jobs", ["book_id"], unique=False)

    op.create_table(
        "collections",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("collection_type", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_collections")),
        sa.UniqueConstraint("name", name=op.f("uq_collections_name")),
    )

    op.create_table(
        "collection_books",
        sa.Column("collection_id", sa.String(length=36), nullable=False),
        sa.Column("book_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            name=op.f("fk_collection_books_book_id_books"),
        ),
        sa.ForeignKeyConstraint(
            ["collection_id"],
            ["collections.id"],
            name=op.f("fk_collection_books_collection_id_collections"),
        ),
        sa.PrimaryKeyConstraint("collection_id", "book_id", name=op.f("pk_collection_books")),
    )

    op.create_table(
        "queries",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("book_scope", sa.Text(), nullable=False),
        sa.Column("response_preview", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_queries")),
    )


def downgrade() -> None:
    op.drop_table("queries")
    op.drop_table("collection_books")
    op.drop_table("collections")
    op.drop_index(op.f("ix_jobs_book_id"), table_name="jobs")
    op.drop_table("jobs")
    op.drop_index(op.f("ix_artifacts_book_id"), table_name="artifacts")
    op.drop_table("artifacts")
    op.drop_index(op.f("ix_chunks_section_id"), table_name="chunks")
    op.drop_index(op.f("ix_chunks_book_id"), table_name="chunks")
    op.drop_table("chunks")
    op.drop_index(op.f("ix_sections_book_id"), table_name="sections")
    op.drop_table("sections")
    op.drop_table("books")
