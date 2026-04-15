from __future__ import annotations

from packages.ingest.adapters.base import SourceAdapter


class AdapterRegistry:
    def __init__(self, adapters: list[SourceAdapter]):
        self.adapters = adapters

    def select(self, *, source_type: str, source_ref: str) -> SourceAdapter:
        for adapter in self.adapters:
            if adapter.can_handle(source_type=source_type, source_ref=source_ref):
                return adapter
        raise ValueError(
            f"No adapter registered for source_type={source_type}, source_ref={source_ref}"
        )
