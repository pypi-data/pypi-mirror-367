# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["Thread"]


class Thread(BaseModel):
    id: str

    created_at: datetime

    deleted_at: Optional[datetime] = None

    updated_at: datetime

    user_id: Optional[str] = None
