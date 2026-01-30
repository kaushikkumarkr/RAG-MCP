"""Search result models."""

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """A search result from the RAG engine."""

    chunk_id: str = Field(description="Chunk identifier")
    content: str = Field(description="Chunk content")
    source: str = Field(description="Source file path")
    source_type: str = Field(description="Type of source")
    relevance_score: float = Field(description="Relevance score 0-1")
    title: str | None = Field(default=None, description="Document title")
    heading: str | None = Field(default=None, description="Nearest heading")
    tags: list[str] = Field(default_factory=list, description="Document tags")
