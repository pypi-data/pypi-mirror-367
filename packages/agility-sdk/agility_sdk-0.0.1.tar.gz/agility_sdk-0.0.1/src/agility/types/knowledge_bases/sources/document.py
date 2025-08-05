# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime

from ...._models import BaseModel

__all__ = ["Document", "Metadata"]


class Metadata(BaseModel):
    key: str

    value: Union[str, float, bool, None] = None


class Document(BaseModel):
    id: str

    content: str

    created_at: datetime

    deleted_at: Optional[datetime] = None

    knowledge_base_id: str

    metadata: List[Metadata]

    source_id: str

    updated_at: datetime
