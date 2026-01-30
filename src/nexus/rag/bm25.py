"""BM25 keyword search."""

from dataclasses import dataclass
from typing import Any

from loguru import logger
from rank_bm25 import BM25Okapi

from nexus.models.document import Chunk
from nexus.storage.metadata import MetadataStore


def tokenize(text: str) -> list[str]:
    """Simple tokenization for BM25."""
    import re
    # Lowercase and split on non-alphanumeric
    tokens = re.findall(r'\b\w+\b', text.lower())
    return tokens


class BM25Index:
    """BM25 index for keyword search."""

    def __init__(self, metadata_store: MetadataStore) -> None:
        """Initialize BM25 index.

        Args:
            metadata_store: Metadata store to load chunks from
        """
        self.metadata_store = metadata_store
        self._index: BM25Okapi | None = None
        self._chunk_ids: list[str] = []
        self._corpus: list[list[str]] = []

    def build_index(self, chunk_ids: list[str] | None = None) -> None:
        """Build or rebuild the BM25 index.

        Args:
            chunk_ids: Optional list of chunk IDs to index. If None, indexes all chunks.
        """
        if chunk_ids:
            chunks = self.metadata_store.get_chunks_by_ids(chunk_ids)
        else:
            # Get all chunks from all documents
            # For now, we iterate through stats to get count
            stats = self.metadata_store.get_stats()
            if stats["chunks"] == 0:
                self._index = None
                self._chunk_ids = []
                self._corpus = []
                return

            # Load all chunks via a simple query
            conn = self.metadata_store._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM chunks")
            all_ids = [row[0] for row in cursor.fetchall()]
            chunks = self.metadata_store.get_chunks_by_ids(all_ids)

        # Tokenize and build index
        self._chunk_ids = [c.id for c in chunks]
        self._corpus = [tokenize(c.content) for c in chunks]

        if self._corpus:
            self._index = BM25Okapi(self._corpus)
            logger.info(f"Built BM25 index with {len(self._chunk_ids)} chunks")
        else:
            self._index = None

    def search(
        self,
        query: str,
        top_k: int = 20,
    ) -> list[tuple[str, float]]:
        """Search using BM25.

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of (chunk_id, score) tuples
        """
        if self._index is None or not self._chunk_ids:
            return []

        query_tokens = tokenize(query)
        scores = self._index.get_scores(query_tokens)

        # Get top-k indices
        scored_indices = list(enumerate(scores))
        scored_indices.sort(key=lambda x: x[1], reverse=True)
        top_indices = scored_indices[:top_k]

        # Return (chunk_id, score) pairs
        results = [
            (self._chunk_ids[idx], float(score))
            for idx, score in top_indices
            if score > 0
        ]

        return results

    def add_chunks(self, chunks: list[Chunk]) -> None:
        """Add chunks to the index.

        Args:
            chunks: Chunks to add
        """
        for chunk in chunks:
            self._chunk_ids.append(chunk.id)
            self._corpus.append(tokenize(chunk.content))

        if self._corpus:
            self._index = BM25Okapi(self._corpus)
