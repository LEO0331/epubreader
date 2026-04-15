from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceMetadata:
    source_type: str
    source_ref: str
    original_filename: str | None = None
    content_type: str | None = None


@dataclass(frozen=True)
class RawSourcePayload:
    metadata: SourceMetadata
    content_bytes: bytes


class SourceAdapter(ABC):
    @abstractmethod
    def can_handle(self, *, source_type: str, source_ref: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def fetch(self, *, source_ref: str, upload_bytes: bytes | None = None) -> RawSourcePayload:
        raise NotImplementedError

    @abstractmethod
    def extract_metadata(self, payload: RawSourcePayload) -> dict[str, str]:
        raise NotImplementedError

    @abstractmethod
    def snapshot(self, *, book_id: str, payload: RawSourcePayload, raw_root: Path) -> Path:
        raise NotImplementedError
