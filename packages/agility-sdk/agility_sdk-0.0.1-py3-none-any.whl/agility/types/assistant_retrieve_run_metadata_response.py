# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel

__all__ = ["AssistantRetrieveRunMetadataResponse"]


class AssistantRetrieveRunMetadataResponse(BaseModel):
    query: str

    response: str

    context: Optional[List[str]] = None

    messages: Optional[List[Dict[str, object]]] = None

    prompt: Optional[str] = None
