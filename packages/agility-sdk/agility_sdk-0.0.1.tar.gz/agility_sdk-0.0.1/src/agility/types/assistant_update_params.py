# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["AssistantUpdateParams", "HardCodedQuery"]


class AssistantUpdateParams(TypedDict, total=False):
    id: Required[str]

    description: Required[str]
    """The description of the assistant"""

    knowledge_base_id: Required[Optional[str]]

    name: Required[str]
    """The name of the assistant"""

    codex_access_key: Optional[str]

    codex_as_cache: bool

    context_limit: Optional[int]
    """The maximum number of context chunks to include in a run."""

    hard_coded_queries: Optional[Iterable[HardCodedQuery]]

    instructions: Optional[str]

    logo_s3_key: Optional[str]
    """S3 object key to the assistant's logo image"""

    logo_text: Optional[str]
    """Text to display alongside the assistant's logo"""

    model: Optional[Literal["gpt-4o"]]

    suggested_questions: List[str]
    """A list of suggested questions that can be asked to the assistant"""

    url_slug: Optional[str]
    """Optional URL suffix - unique identifier for the assistant's endpoint"""


class HardCodedQuery(TypedDict, total=False):
    query: Required[str]

    response: Required[str]

    context: Optional[List[str]]

    messages: Optional[Iterable[Dict[str, object]]]

    prompt: Optional[str]
