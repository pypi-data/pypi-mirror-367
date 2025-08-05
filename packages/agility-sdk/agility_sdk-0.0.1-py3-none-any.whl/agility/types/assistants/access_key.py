# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["AccessKey"]


class AccessKey(BaseModel):
    id: str

    token: str

    assistant_id: str

    created_at: datetime

    creator_user_id: str

    description: Optional[str] = None

    expires_at: Optional[datetime] = None

    last_used_at: Optional[datetime] = None

    name: str

    status: Literal["active", "expired", "inactive", "revoked"]

    updated_at: datetime
