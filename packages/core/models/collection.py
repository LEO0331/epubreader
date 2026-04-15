from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from packages.core.models.enums import CollectionType


class Collection(BaseModel):
    id: str
    name: str
    collection_type: CollectionType = CollectionType.USER
    created_at: datetime
