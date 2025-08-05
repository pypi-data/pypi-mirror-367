# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["Message", "Metadata", "MetadataScores", "MetadataScoresLog"]


class MetadataScoresLog(BaseModel):
    explanation: Optional[str] = None


class MetadataScores(BaseModel):
    is_bad: Optional[bool] = None

    log: Optional[MetadataScoresLog] = None

    score: Optional[float] = None

    triggered: Optional[bool] = None

    triggered_escalation: Optional[bool] = None

    triggered_guardrail: Optional[bool] = None


class Metadata(BaseModel):
    citations: Optional[List[str]] = None

    escalated_to_sme: Optional[bool] = None

    guardrailed: Optional[bool] = None

    is_bad_response: Optional[bool] = None

    is_expert_answer: Optional[bool] = None

    original_llm_response: Optional[str] = None

    scores: Optional[Dict[str, MetadataScores]] = None

    trustworthiness_explanation: Optional[str] = None

    trustworthiness_score: Optional[float] = None


class Message(BaseModel):
    id: str

    content: str

    created_at: datetime

    metadata: Metadata

    role: Literal["user", "assistant"]

    thread_id: str

    updated_at: datetime

    deleted_at: Optional[datetime] = None
