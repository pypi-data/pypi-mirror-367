# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["Assistant"]


class Assistant(BaseModel):
    id: str

    created_at: datetime

    deleted_at: Optional[datetime] = None

    description: str
    """The description of the assistant"""

    name: str
    """The name of the assistant"""

    updated_at: datetime

    logo_s3_key: Optional[str] = None
    """S3 object key to the assistant's logo image"""

    logo_text: Optional[str] = None
    """Text to display alongside the assistant's logo"""

    suggested_questions: Optional[List[str]] = None
    """A list of suggested questions that can be asked to the assistant"""

    url_slug: Optional[str] = None
    """Optional URL suffix - unique identifier for the assistant's endpoint"""
