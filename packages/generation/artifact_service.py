from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from packages.generation.qa_generator import generate_synthetic_qa
from packages.generation.skill_generator import generate_skill
from packages.generation.summary_generator import generate_summary
from packages.generation.wiki_generator import generate_wiki
from packages.llm.base import LLMProvider
from packages.prompts.loader import PromptLoader
from packages.storage.repositories.artifacts_repo import ArtifactsRepository
from packages.storage.repositories.books_repo import BooksRepository
from packages.storage.repositories.chunks_repo import ChunksRepository


class ArtifactService:
    def __init__(self, session: Session, data_root: str, prompts_dir: str, provider: LLMProvider):
        self.session = session
        self.data_root = Path(data_root)
        self.prompts = PromptLoader(prompts_dir)
        self.provider = provider
        self.books = BooksRepository(session)
        self.chunks = ChunksRepository(session)
        self.artifacts = ArtifactsRepository(session)

    def build_for_book(
        self,
        *,
        book_id: str,
        include_skill: bool = False,
    ) -> dict[str, object]:
        book = self.books.get(book_id)
        if book is None:
            raise ValueError(f"Book not found: {book_id}")

        chunk_rows = self.chunks.list_by_book(book_id, limit=5000, offset=0)
        chunk_records: list[dict[str, object]] = [
            {
                "id": row.id,
                "text": row.text,
            }
            for row in chunk_rows
        ]
        chunk_texts = [str(row["text"]) for row in chunk_records]

        summary = generate_summary(
            provider=self.provider,
            prompt_loader=self.prompts,
            chunk_texts=chunk_texts,
        )
        wiki = generate_wiki(
            provider=self.provider,
            prompt_loader=self.prompts,
            summary_text=summary["content"],
        )
        qa = generate_synthetic_qa(
            provider=self.provider,
            prompt_loader=self.prompts,
            chunk_records=chunk_records,
        )
        skill = generate_skill(
            provider=self.provider,
            prompt_loader=self.prompts,
            summary_text=summary["content"],
            force=include_skill,
        )

        out_dir = self.data_root / "artifacts" / book_id
        out_dir.mkdir(parents=True, exist_ok=True)

        summary_path = out_dir / "summary.md"
        wiki_path = out_dir / "wiki.md"
        qa_path = out_dir / "qa.jsonl"

        summary_path.write_text(summary["content"], encoding="utf-8")
        wiki_path.write_text(wiki["content"], encoding="utf-8")

        qa_items_any = qa.get("items")
        qa_items: list[dict[str, str]] = qa_items_any if isinstance(qa_items_any, list) else []
        with qa_path.open("w", encoding="utf-8") as handle:
            for item in qa_items:
                handle.write(json.dumps(item, ensure_ascii=False) + "\n")

        self._save_artifact(
            book_id=book_id,
            artifact_type="summary",
            path=summary_path,
            metadata={k: v for k, v in summary.items()},
        )
        self._save_artifact(
            book_id=book_id,
            artifact_type="wiki",
            path=wiki_path,
            metadata={k: v for k, v in wiki.items()},
        )
        self._save_artifact(
            book_id=book_id,
            artifact_type="qa",
            path=qa_path,
            metadata={k: v for k, v in qa.items()},
        )

        saved: dict[str, str] = {
            "summary": str(summary_path),
            "wiki": str(wiki_path),
            "qa": str(qa_path),
        }

        if skill is not None:
            skill_path = out_dir / "skill.md"
            skill_path.write_text(skill["content"], encoding="utf-8")
            self._save_artifact(
                book_id=book_id,
                artifact_type="skill",
                path=skill_path,
                metadata={k: v for k, v in skill.items()},
            )
            saved["skill"] = str(skill_path)

        sample_dir = Path("sample") / "miz-500"
        sample_dir.mkdir(parents=True, exist_ok=True)
        (sample_dir / "summary.md").write_text(summary["content"], encoding="utf-8")
        (sample_dir / "wiki.md").write_text(wiki["content"], encoding="utf-8")
        with (sample_dir / "qa.jsonl").open("w", encoding="utf-8") as handle:
            for item in qa_items:
                handle.write(json.dumps(item, ensure_ascii=False) + "\n")
        if skill is not None:
            (sample_dir / "skill.md").write_text(skill["content"], encoding="utf-8")

        manifest_path = out_dir / "artifact_manifest.json"
        manifest_path.write_text(json.dumps(saved, indent=2), encoding="utf-8")

        self.session.commit()
        return {"book_id": book_id, "artifacts": saved}

    def list_artifacts(self, *, book_id: str) -> list[dict[str, object]]:
        rows = self.artifacts.list_by_book(book_id)
        out: list[dict[str, object]] = []
        for row in rows:
            out.append(
                {
                    "id": row.id,
                    "book_id": row.book_id,
                    "artifact_type": row.artifact_type,
                    "path": row.path,
                    "metadata": json.loads(row.metadata_json),
                    "created_at": row.created_at.isoformat(),
                }
            )
        return out

    def get_artifact(self, *, book_id: str, artifact_type: str) -> dict[str, object] | None:
        row = self.artifacts.get_latest_by_type(book_id=book_id, artifact_type=artifact_type)
        if row is None:
            return None

        path = Path(row.path)
        return {
            "id": row.id,
            "book_id": row.book_id,
            "artifact_type": row.artifact_type,
            "path": row.path,
            "content": path.read_text(encoding="utf-8") if path.exists() else None,
            "metadata": json.loads(row.metadata_json),
            "created_at": row.created_at.isoformat(),
        }

    def _save_artifact(
        self,
        *,
        book_id: str,
        artifact_type: str,
        path: Path,
        metadata: dict[str, object],
    ) -> None:
        metadata_str = {str(k): str(v) for k, v in metadata.items()}
        self.artifacts.create(
            artifact_id=str(uuid4()),
            book_id=book_id,
            artifact_type=artifact_type,
            path=str(path),
            metadata=metadata_str,
        )
