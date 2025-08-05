# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["MessageCreateParams", "Metadata", "MetadataScores", "MetadataScoresLog"]


class MessageCreateParams(TypedDict, total=False):
    content: Required[str]

    metadata: Required[Optional[Metadata]]

    role: Required[Literal["user", "assistant"]]


class MetadataScoresLog(TypedDict, total=False):
    explanation: Optional[str]


class MetadataScores(TypedDict, total=False):
    is_bad: Optional[bool]

    log: Optional[MetadataScoresLog]

    score: Optional[float]

    triggered: Optional[bool]

    triggered_escalation: Optional[bool]

    triggered_guardrail: Optional[bool]


class Metadata(TypedDict, total=False):
    citations: Optional[List[str]]

    escalated_to_sme: Optional[bool]

    guardrailed: Optional[bool]

    is_bad_response: Optional[bool]

    is_expert_answer: Optional[bool]

    original_llm_response: Optional[str]

    scores: Optional[Dict[str, MetadataScores]]

    trustworthiness_explanation: Optional[str]

    trustworthiness_score: Optional[float]
