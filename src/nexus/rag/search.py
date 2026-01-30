"""RAG search engine."""

from typing import Any

from loguru import logger

from nexus.config import Config
from nexus.models.search import SearchResult
from nexus.rag.embedder import Embedder
from nexus.storage.metadata import MetadataStore
from nexus.storage.vectors import VectorStore


class SearchEngine:
    """RAG search engine combining vector and keyword search."""

    def __init__(
        self,
        embedder: Embedder,
        metadata_store: MetadataStore,
        vector_store: VectorStore,
        top_k: int = 20,
    ) -> None:
        """Initialize search engine.

        Args:
            embedder: Embedding service
            metadata_store: Metadata storage
            vector_store: Vector storage
            top_k: Number of results to retrieve
        """
        self.embedder = embedder
        self.metadata_store = metadata_store
        self.vector_store = vector_store
        self.top_k = top_k

    def search(
        self,
        query: str,
        top_k: int | None = None,
        filters: dict[str, Any] | None = None,
        source_type: str | None = None,
        tags: list[str] | None = None,
    ) -> list[SearchResult]:
        """Search for relevant chunks.

        Args:
            query: Search query
            top_k: Number of results (defaults to self.top_k)
            filters: Additional metadata filters
            source_type: Filter by source type
            tags: Filter by tags

        Returns:
            List of search results
        """
        k = top_k or self.top_k

        # Build filters
        search_filters = filters.copy() if filters else {}
        if source_type:
            search_filters["source_type"] = source_type

        # Embed query
        query_embedding = self.embedder.embed_text(query)

        # Vector search
        vector_results = self.vector_store.search(
            query_vector=query_embedding,
            limit=k,
            filters=search_filters if search_filters else None,
        )

        # Get full chunk data from metadata store
        chunk_ids = [r["id"] for r in vector_results]
        chunks = self.metadata_store.get_chunks_by_ids(chunk_ids)

        # Build results with scores
        chunk_map = {c.id: c for c in chunks}
        results: list[SearchResult] = []

        for vr in vector_results:
            chunk_id = vr["id"]
            chunk = chunk_map.get(chunk_id)
            if not chunk:
                continue

            # Filter by tags if specified
            if tags:
                chunk_tags = chunk.metadata.tags or []
                if not any(t in chunk_tags for t in tags):
                    continue

            result = SearchResult(
                chunk_id=chunk.id,
                content=chunk.content,
                source=chunk.metadata.source_path,
                source_type=chunk.metadata.source_type,
                relevance_score=vr["score"],
                title=chunk.metadata.title,
                heading=chunk.metadata.heading,
                tags=chunk.metadata.tags,
            )
            results.append(result)

        logger.debug(f"Search for '{query}' returned {len(results)} results")
        return results

    def search_by_source(
        self,
        query: str,
        source_path: str,
        top_k: int | None = None,
    ) -> list[SearchResult]:
        """Search within a specific source.

        Args:
            query: Search query
            source_path: Path to source
            top_k: Number of results

        Returns:
            List of search results
        """
        return self.search(
            query=query,
            top_k=top_k,
            filters={"source_path": source_path},
        )

    def similar_chunks(
        self,
        chunk_id: str,
        top_k: int = 5,
    ) -> list[SearchResult]:
        """Find chunks similar to a given chunk.

        Args:
            chunk_id: ID of chunk to find similar to
            top_k: Number of results

        Returns:
            List of similar chunks
        """
        # Get the chunk
        chunk = self.metadata_store.get_chunk(chunk_id)
        if not chunk:
            return []

        # Use its content as query
        return self.search(query=chunk.content, top_k=top_k + 1)[1:]  # Exclude self
