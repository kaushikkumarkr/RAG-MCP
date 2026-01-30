"""Source models."""

from datetime import datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    """Types of knowledge sources."""

    MARKDOWN = "markdown"
    PDF = "pdf"
    NOTE = "note"
    READWISE = "readwise"
    WEBPAGE = "webpage"


class Source(BaseModel):
    """A knowledge source."""

    id: str = Field(description="Unique source identifier")
    path: str = Field(description="Path or identifier for the source")
    source_type: SourceType = Field(description="Type of source")
    title: str | None = Field(default=None, description="Source title")
    document_count: int = Field(default=0, description="Number of documents")
    chunk_count: int = Field(default=0, description="Number of chunks")
    last_indexed: datetime | None = Field(default=None, description="Last indexing time")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
