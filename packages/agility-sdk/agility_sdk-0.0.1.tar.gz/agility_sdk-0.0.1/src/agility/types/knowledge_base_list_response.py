# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated, TypeAlias

from .._utils import PropertyInfo
from .._models import BaseModel

__all__ = [
    "KnowledgeBaseListResponse",
    "IngestionPipelineParams",
    "IngestionPipelineParamsCurate",
    "IngestionPipelineParamsCurateSteps",
    "IngestionPipelineParamsCurateStepsRemoveExactDuplicatesParams",
    "IngestionPipelineParamsCurateStepsTagExactDuplicatesParams",
    "IngestionPipelineParamsCurateStepsPostpendContentParams",
    "IngestionPipelineParamsCurateStepsRemoveEmbeddedImagesParams",
    "IngestionPipelineParamsCurateDocumentStore",
    "IngestionPipelineParamsTransform",
    "IngestionPipelineParamsTransformSteps",
    "IngestionPipelineParamsTransformStepsRecursiveCharacterSplitterV0Params",
    "IngestionPipelineParamsTransformStepsCharacterSplitterV0Params",
    "IngestionPipelineParamsTransformStepsSemanticMergeSplitterV0Params",
    "IngestionPipelineParamsTransformStepsMarkdownNodeExpanderParams",
    "IngestionPipelineParamsTransformStepsNodeSummarizerV0Params",
    "IngestionPipelineParamsTransformStepsNoopParams",
    "IngestionPipelineParamsVectorStore",
]


class IngestionPipelineParamsCurateStepsRemoveExactDuplicatesParams(BaseModel):
    name: Optional[Literal["remove_exact_duplicates.v0"]] = None


class IngestionPipelineParamsCurateStepsTagExactDuplicatesParams(BaseModel):
    name: Optional[Literal["tag_exact_duplicates.v0"]] = None


class IngestionPipelineParamsCurateStepsPostpendContentParams(BaseModel):
    postpend_value: str
    """The value to postpend to the content."""

    name: Optional[Literal["postpend_content.v0"]] = None


class IngestionPipelineParamsCurateStepsRemoveEmbeddedImagesParams(BaseModel):
    name: Optional[Literal["remove_embedded_images.v0"]] = None


IngestionPipelineParamsCurateSteps: TypeAlias = Annotated[
    Union[
        IngestionPipelineParamsCurateStepsRemoveExactDuplicatesParams,
        IngestionPipelineParamsCurateStepsTagExactDuplicatesParams,
        IngestionPipelineParamsCurateStepsPostpendContentParams,
        IngestionPipelineParamsCurateStepsRemoveEmbeddedImagesParams,
    ],
    PropertyInfo(discriminator="name"),
]


class IngestionPipelineParamsCurate(BaseModel):
    steps: Optional[Dict[str, IngestionPipelineParamsCurateSteps]] = None


class IngestionPipelineParamsCurateDocumentStore(BaseModel):
    document_tags: Optional[Dict[str, str]] = None


class IngestionPipelineParamsTransformStepsRecursiveCharacterSplitterV0Params(BaseModel):
    chunk_overlap: Optional[int] = None

    chunk_size: Optional[int] = None

    name: Optional[Literal["splitters.recursive_character.v0"]] = None


class IngestionPipelineParamsTransformStepsCharacterSplitterV0Params(BaseModel):
    chunk_overlap: Optional[int] = None

    chunk_size: Optional[int] = None

    name: Optional[Literal["splitters.character.v0"]] = None


class IngestionPipelineParamsTransformStepsSemanticMergeSplitterV0Params(BaseModel):
    appending_threshold: Optional[float] = None

    initial_threshold: Optional[float] = None

    max_chunk_size: Optional[int] = None

    merging_range: Optional[int] = None

    merging_threshold: Optional[float] = None

    name: Optional[Literal["splitters.semantic_merge.v0"]] = None


class IngestionPipelineParamsTransformStepsMarkdownNodeExpanderParams(BaseModel):
    code_block_pattern: Optional[str] = None
    """A regex pattern used to identify code blocks in markdown.

    Matches both multi-line code blocks enclosed in triple backticks and inline code
    wrapped in single backticks.
    """

    name: Optional[Literal["node_expander.v0"]] = None
    """The version identifier for the node expander."""

    section_delimiter_pattern: Optional[str] = None
    """A regex pattern used to identify markdown sections.

    Matches headers of level 1 to 6, capturing the section title and content until
    the next header.
    """


class IngestionPipelineParamsTransformStepsNodeSummarizerV0Params(BaseModel):
    expected_summary_tokens: Optional[int] = None

    max_prompt_input_tokens: Optional[int] = None

    model: Optional[str] = None

    name: Optional[Literal["node_summarizer.v0"]] = None


class IngestionPipelineParamsTransformStepsNoopParams(BaseModel):
    name: Optional[Literal["noop"]] = None


IngestionPipelineParamsTransformSteps: TypeAlias = Union[
    IngestionPipelineParamsTransformStepsRecursiveCharacterSplitterV0Params,
    IngestionPipelineParamsTransformStepsCharacterSplitterV0Params,
    IngestionPipelineParamsTransformStepsSemanticMergeSplitterV0Params,
    IngestionPipelineParamsTransformStepsMarkdownNodeExpanderParams,
    IngestionPipelineParamsTransformStepsNodeSummarizerV0Params,
    IngestionPipelineParamsTransformStepsNoopParams,
]


class IngestionPipelineParamsTransform(BaseModel):
    steps: Optional[Dict[str, IngestionPipelineParamsTransformSteps]] = None


class IngestionPipelineParamsVectorStore(BaseModel):
    weaviate_collection_name: str
    """The name of the Weaviate collection to use for storing documents.

    Must start with AgilityKB and be valid.
    """

    node_tags: Optional[Dict[str, str]] = None


class IngestionPipelineParams(BaseModel):
    curate: IngestionPipelineParamsCurate
    """Curate params.

    Defines full curation pipeline, as an ordered dict of named curation steps.
    Order of steps _does_ matter -- they are executed in the order defined.
    """

    curate_document_store: IngestionPipelineParamsCurateDocumentStore
    """Document store params."""

    transform: IngestionPipelineParamsTransform
    """Transform params.

    Defines full transform pipeline, as an ordered dict of named transform steps.
    Order of steps _does_ matter -- they are executed in the order defined.
    """

    vector_store: IngestionPipelineParamsVectorStore
    """Vector store params."""


class KnowledgeBaseListResponse(BaseModel):
    id: str

    created_at: datetime

    deleted_at: Optional[datetime] = None

    description: str

    ingestion_pipeline_params: IngestionPipelineParams
    """Knowledge base pipeline params.

    Parameters defined on the knowledge-base level for a pipeline.
    """

    name: str

    status: Literal["pending", "syncing", "synced", "failed"]
    """Source status enum."""

    updated_at: datetime
