# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["SourceStatusResponse"]


class SourceStatusResponse(BaseModel):
    status: Literal["pending", "syncing", "synced", "failed"]
    """Source status enum."""

    updated_at: datetime
