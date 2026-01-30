"""Storage interface abstraction."""

from abc import ABC, abstractmethod
from typing import Any

from nexus.models.document import Chunk, Document
from nexus.models.source import Source


class BaseMetadataStore(ABC):
    """Abstract base class for metadata storage."""

    @abstractmethod
    def add_source(self, source: Source) -> None:
        """Add a source."""
        ...

    @abstractmethod
    def get_source(self, source_id: str) -> Source | None:
        """Get a source by ID."""
        ...

    @abstractmethod
    def list_sources(self) -> list[Source]:
        """List all sources."""
        ...

    @abstractmethod
    def add_document(self, doc: Document) -> None:
        """Add a document."""
        ...

    @abstractmethod
    def get_document(self, doc_id: str) -> Document | None:
        """Get a document by ID."""
        ...

    @abstractmethod
    def add_chunk(self, chunk: Chunk) -> None:
        """Add a chunk."""
        ...

    @abstractmethod
    def get_chunk(self, chunk_id: str) -> Chunk | None:
        """Get a chunk by ID."""
        ...

    @abstractmethod
    def get_chunks_by_ids(self, chunk_ids: list[str]) -> list[Chunk]:
        """Get multiple chunks by IDs."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Close the store."""
        ...


class BaseVectorStore(ABC):
    """Abstract base class for vector storage."""

    @abstractmethod
    def add_vectors(
        self,
        ids: list[str],
        vectors: list[list[float]],
        payloads: list[dict[str, Any]] | None = None,
    ) -> None:
        """Add vectors to the store."""
        ...

    @abstractmethod
    def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors."""
        ...

    @abstractmethod
    def delete_vectors(self, ids: list[str]) -> None:
        """Delete vectors by IDs."""
        ...

    @abstractmethod
    def get_count(self) -> int:
        """Get total vector count."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Close the store."""
        ...
