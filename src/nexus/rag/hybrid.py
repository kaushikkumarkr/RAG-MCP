"""Hybrid search with Reciprocal Rank Fusion."""

from typing import Any

from loguru import logger

from nexus.config import Config
from nexus.models.search import SearchResult
from nexus.rag.bm25 import BM25Index
from nexus.rag.embedder import Embedder
from nexus.storage.metadata import MetadataStore
from nexus.storage.vectors import VectorStore


def reciprocal_rank_fusion(
    result_lists: list[list[tuple[str, float]]],
    k: int = 60,
) -> list[tuple[str, float]]:
    """Combine multiple result lists using RRF.

    Args:
        result_lists: List of (id, score) lists from different retrieval methods
        k: RRF constant (default 60)

    Returns:
        Combined list of (id, fused_score) sorted by score descending
    """
    scores: dict[str, float] = {}

    for results in result_lists:
        for rank, (doc_id, _) in enumerate(results, start=1):
            if doc_id not in scores:
                scores[doc_id] = 0.0
            scores[doc_id] += 1.0 / (k + rank)

    # Sort by score
    sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_results


class HybridSearchEngine:
    """Hybrid search combining vector and BM25 with optional reranking."""

    def __init__(
        self,
        embedder: Embedder,
        metadata_store: MetadataStore,
        vector_store: VectorStore,
        bm25_index: BM25Index | None = None,
        top_k: int = 20,
        hybrid_alpha: float = 0.5,
        use_reranking: bool = False,
        rerank_top_k: int = 5,
    ) -> None:
        """Initialize hybrid search engine.

        Args:
            embedder: Embedding service
            metadata_store: Metadata storage
            vector_store: Vector storage
            bm25_index: BM25 index (created if not provided)
            top_k: Number of results per retrieval method
            hybrid_alpha: Weight for vector search (1.0 = all vector, 0.0 = all BM25)
            use_reranking: Whether to use cross-encoder reranking
            rerank_top_k: Number of results after reranking
        """
        self.embedder = embedder
        self.metadata_store = metadata_store
        self.vector_store = vector_store
        self.bm25_index = bm25_index or BM25Index(metadata_store)
        self.top_k = top_k
        self.hybrid_alpha = hybrid_alpha
        self.use_reranking = use_reranking
        self.rerank_top_k = rerank_top_k

    def build_bm25_index(self) -> None:
        """Build or rebuild the BM25 index."""
        self.bm25_index.build_index()

    def search(
        self,
        query: str,
        top_k: int | None = None,
        filters: dict[str, Any] | None = None,
        source_type: str | None = None,
        tags: list[str] | None = None,
        use_hybrid: bool = True,
    ) -> list[SearchResult]:
        """Perform hybrid search.

        Args:
            query: Search query
            top_k: Number of final results
            filters: Metadata filters for vector search
            source_type: Filter by source type
            tags: Filter by tags
            use_hybrid: Whether to use hybrid (True) or vector-only (False)

        Returns:
            List of search results
        """
        k = top_k or self.top_k

        # Build filters
        search_filters = filters.copy() if filters else {}
        if source_type:
            search_filters["source_type"] = source_type

        # Vector search
        query_embedding = self.embedder.embed_text(query)
        vector_results = self.vector_store.search(
            query_vector=query_embedding,
            limit=k * 2,  # Get more for fusion
            filters=search_filters if search_filters else None,
        )
        vector_list = [(r["id"], r["score"]) for r in vector_results]

        # Combine results
        if use_hybrid and self.bm25_index._index is not None:
            # BM25 search
            bm25_results = self.bm25_index.search(query, top_k=k * 2)

            # RRF fusion
            fused = reciprocal_rank_fusion([vector_list, bm25_results])
            result_ids = [doc_id for doc_id, _ in fused[:k]]
            scores = {doc_id: score for doc_id, score in fused}
        else:
            result_ids = [doc_id for doc_id, _ in vector_list[:k]]
            scores = {doc_id: score for doc_id, score in vector_list}

        # Get full chunk data
        chunks = self.metadata_store.get_chunks_by_ids(result_ids)
        chunk_map = {c.id: c for c in chunks}

        # Build results
        results: list[SearchResult] = []
        for chunk_id in result_ids:
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
                relevance_score=scores.get(chunk_id, 0.0),
                title=chunk.metadata.title,
                heading=chunk.metadata.heading,
                tags=chunk.metadata.tags,
            )
            results.append(result)

        # Reranking (if enabled and cross-encoder available)
        if self.use_reranking and len(results) > self.rerank_top_k:
            results = self._rerank(query, results)[:self.rerank_top_k]

        logger.debug(f"Hybrid search for '{query}' returned {len(results)} results")
        return results

    def _rerank(self, query: str, results: list[SearchResult]) -> list[SearchResult]:
        """Rerank results using cross-encoder (or semantic similarity).

        For now, uses embedder similarity as a simple reranker.
        Can be extended to use a proper cross-encoder model.
        """
        # Calculate similarity scores with query
        scored = []
        for result in results:
            sim = self.embedder.similarity(query, result.content)
            scored.append((result, sim))

        # Sort by similarity
        scored.sort(key=lambda x: x[1], reverse=True)

        # Update scores and return
        reranked = []
        for result, sim in scored:
            result.relevance_score = sim
            reranked.append(result)

        return reranked
