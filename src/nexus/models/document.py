"""Document and Chunk models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):
    """Metadata for a chunk."""

    source_path: str = Field(description="Path to source file")
    source_type: str = Field(description="Type of source: markdown, pdf, etc.")
    start_line: int | None = Field(default=None, description="Start line in source")
    end_line: int | None = Field(default=None, description="End line in source")
    heading: str | None = Field(default=None, description="Nearest heading")
    tags: list[str] = Field(default_factory=list, description="Tags from frontmatter")
    title: str | None = Field(default=None, description="Document title")
    author: str | None = Field(default=None, description="Document author")
    created_at: datetime | None = Field(default=None, description="Creation date")
    extra: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class Chunk(BaseModel):
    """A chunk of text from a document."""

    id: str = Field(description="Unique chunk identifier")
    content: str = Field(description="Chunk text content")
    document_id: str = Field(description="Parent document ID")
    metadata: ChunkMetadata = Field(description="Chunk metadata")
    embedding: list[float] | None = Field(default=None, description="Embedding vector")
    chunk_index: int = Field(default=0, description="Position in document")


class Document(BaseModel):
    """A document in the knowledge base."""

    id: str = Field(description="Unique document identifier")
    source_path: str = Field(description="Path to source file")
    source_type: str = Field(description="Type of source")
    title: str | None = Field(default=None, description="Document title")
    content: str = Field(description="Full document content")
    chunks: list[Chunk] = Field(default_factory=list, description="Document chunks")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    indexed_at: datetime = Field(default_factory=datetime.now, description="Indexing timestamp")
    content_hash: str | None = Field(default=None, description="Hash for change detection")
