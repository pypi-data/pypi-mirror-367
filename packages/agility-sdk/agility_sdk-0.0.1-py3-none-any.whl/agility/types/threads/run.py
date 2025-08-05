# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["Run", "HardCodedQuery", "Usage"]


class HardCodedQuery(BaseModel):
    query: str

    response: str

    context: Optional[List[str]] = None

    messages: Optional[List[Dict[str, object]]] = None

    prompt: Optional[str] = None


class Usage(BaseModel):
    completion_tokens: int

    prompt_tokens: int

    total_tokens: int


class Run(BaseModel):
    id: str

    assistant_id: str

    created_at: datetime

    status: Literal["pending", "in_progress", "completed", "failed", "canceled", "expired"]

    thread_id: str

    updated_at: datetime

    additional_instructions: Optional[str] = None

    codex_access_key: Optional[str] = None

    codex_as_cache: Optional[bool] = None

    context_limit: Optional[int] = None
    """The maximum number of context chunks to include."""

    deleted_at: Optional[datetime] = None

    hard_coded_queries: Optional[List[HardCodedQuery]] = None

    instructions: Optional[str] = None

    knowledge_base_id: Optional[str] = None

    last_error: Optional[str] = None

    model: Optional[Literal["gpt-4o"]] = None

    usage: Optional[Usage] = None
