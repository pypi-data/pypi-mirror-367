# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["AssistantWithConfig", "HardCodedQuery"]


class HardCodedQuery(BaseModel):
    query: str

    response: str

    context: Optional[List[str]] = None

    messages: Optional[List[Dict[str, object]]] = None

    prompt: Optional[str] = None


class AssistantWithConfig(BaseModel):
    id: str

    created_at: datetime

    deleted_at: Optional[datetime] = None

    description: str
    """The description of the assistant"""

    knowledge_base_id: Optional[str] = None

    name: str
    """The name of the assistant"""

    updated_at: datetime

    codex_access_key: Optional[str] = None

    codex_as_cache: Optional[bool] = None

    context_limit: Optional[int] = None
    """The maximum number of context chunks to include in a run."""

    hard_coded_queries: Optional[List[HardCodedQuery]] = None

    instructions: Optional[str] = None

    logo_s3_key: Optional[str] = None
    """S3 object key to the assistant's logo image"""

    logo_text: Optional[str] = None
    """Text to display alongside the assistant's logo"""

    model: Optional[Literal["gpt-4o"]] = None

    suggested_questions: Optional[List[str]] = None
    """A list of suggested questions that can be asked to the assistant"""

    url_slug: Optional[str] = None
    """Optional URL suffix - unique identifier for the assistant's endpoint"""
