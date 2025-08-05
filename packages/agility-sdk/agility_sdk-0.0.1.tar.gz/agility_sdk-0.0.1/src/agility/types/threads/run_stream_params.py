# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = [
    "RunStreamParams",
    "AdditionalMessage",
    "AdditionalMessageMetadata",
    "AdditionalMessageMetadataScores",
    "AdditionalMessageMetadataScoresLog",
    "HardCodedQuery",
]


class RunStreamParams(TypedDict, total=False):
    assistant_id: Required[str]

    additional_instructions: Optional[str]

    additional_messages: Iterable[AdditionalMessage]

    codex_access_key: Optional[str]

    codex_as_cache: Optional[bool]

    context_limit: Optional[int]
    """The maximum number of context chunks to include."""

    hard_coded_queries: Optional[Iterable[HardCodedQuery]]

    instructions: Optional[str]

    knowledge_base_id: Optional[str]

    model: Optional[Literal["gpt-4o"]]


class AdditionalMessageMetadataScoresLog(TypedDict, total=False):
    explanation: Optional[str]


class AdditionalMessageMetadataScores(TypedDict, total=False):
    is_bad: Optional[bool]

    log: Optional[AdditionalMessageMetadataScoresLog]

    score: Optional[float]

    triggered: Optional[bool]

    triggered_escalation: Optional[bool]

    triggered_guardrail: Optional[bool]


class AdditionalMessageMetadata(TypedDict, total=False):
    citations: Optional[List[str]]

    escalated_to_sme: Optional[bool]

    guardrailed: Optional[bool]

    is_bad_response: Optional[bool]

    is_expert_answer: Optional[bool]

    original_llm_response: Optional[str]

    scores: Optional[Dict[str, AdditionalMessageMetadataScores]]

    trustworthiness_explanation: Optional[str]

    trustworthiness_score: Optional[float]


class AdditionalMessage(TypedDict, total=False):
    content: Required[str]

    metadata: Required[AdditionalMessageMetadata]

    role: Required[Literal["user", "assistant"]]

    thread_id: Required[str]


class HardCodedQuery(TypedDict, total=False):
    query: Required[str]

    response: Required[str]

    context: Optional[List[str]]

    messages: Optional[Iterable[Dict[str, object]]]

    prompt: Optional[str]
