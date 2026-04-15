from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy.orm import Session

from packages.storage.db.models import ArtifactORM


class ArtifactsRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        *,
        artifact_id: str,
        book_id: str,
        artifact_type: str,
        path: str,
        metadata: dict[str, str] | None = None,
    ) -> ArtifactORM:
        artifact = ArtifactORM(
            id=artifact_id,
            book_id=book_id,
            artifact_type=artifact_type,
            path=path,
            metadata_json=json.dumps(metadata or {}),
            created_at=datetime.utcnow(),
        )
        self.session.add(artifact)
        self.session.flush()
        return artifact

    def list_by_book(self, book_id: str) -> list[ArtifactORM]:
        return (
            self.session.query(ArtifactORM)
            .filter(ArtifactORM.book_id == book_id)
            .order_by(ArtifactORM.created_at.desc())
            .all()
        )

    def get_latest_by_type(self, *, book_id: str, artifact_type: str) -> ArtifactORM | None:
        return (
            self.session.query(ArtifactORM)
            .filter(ArtifactORM.book_id == book_id)
            .filter(ArtifactORM.artifact_type == artifact_type)
            .order_by(ArtifactORM.created_at.desc())
            .first()
        )
