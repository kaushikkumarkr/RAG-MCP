"""Qdrant vector store wrapper."""

import hashlib
from pathlib import Path
from typing import Any

from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
)

from nexus.exceptions import StorageError


def _string_to_int_id(s: str) -> int:
    """Convert string ID to integer ID for Qdrant."""
    # Use first 16 hex chars of MD5 hash, convert to int
    return int(hashlib.md5(s.encode()).hexdigest()[:16], 16)


class VectorStore:
    """Qdrant-based vector storage for embeddings."""

    def __init__(
        self,
        collection_name: str = "nexus_knowledge",
        path: Path | None = None,
        url: str | None = None,
        embedding_dim: int = 768,
    ) -> None:
        """Initialize vector store.

        Args:
            collection_name: Name of the Qdrant collection
            path: Path for embedded Qdrant storage
            url: URL for Qdrant server (if using server mode)
            embedding_dim: Dimension of embedding vectors
        """
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim

        if url:
            self.client = QdrantClient(url=url)
            logger.info(f"Connected to Qdrant server at {url}")
        else:
            storage_path = path or Path("~/.nexus/qdrant").expanduser()
            storage_path.mkdir(parents=True, exist_ok=True)
            self.client = QdrantClient(path=str(storage_path))
            logger.info(f"Using embedded Qdrant at {storage_path}")

        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Ensure collection exists with correct configuration."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Created collection '{self.collection_name}'")
        else:
            logger.debug(f"Collection '{self.collection_name}' already exists")

    def add_vectors(
        self,
        ids: list[str],
        vectors: list[list[float]],
        payloads: list[dict[str, Any]] | None = None,
    ) -> None:
        """Add vectors to the collection.

        Args:
            ids: Unique identifiers for each vector (strings, converted to int internally)
            vectors: Embedding vectors
            payloads: Optional metadata for each vector
        """
        if len(ids) != len(vectors):
            raise StorageError("ids and vectors must have the same length")

        if payloads and len(payloads) != len(ids):
            raise StorageError("payloads must have the same length as ids")

        # Build points with int IDs and original string ID in payload
        points = []
        for i, (str_id, vector) in enumerate(zip(ids, vectors)):
            int_id = _string_to_int_id(str_id)
            payload = (payloads[i] if payloads else {}).copy()
            payload["_original_id"] = str_id  # Store original string ID
            points.append(
                PointStruct(
                    id=int_id,
                    vector=vector,
                    payload=payload,
                )
            )

        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
            logger.debug(f"Added {len(points)} vectors to collection")
        except Exception as e:
            raise StorageError(f"Failed to add vectors: {e}") from e

    def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        filters: dict[str, Any] | None = None,
        score_threshold: float | None = None,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors.

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            filters: Optional metadata filters
            score_threshold: Minimum score threshold

        Returns:
            List of results with id, score, and payload
        """
        qdrant_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=value))
                )
            qdrant_filter = Filter(must=conditions)

        try:
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
                query_filter=qdrant_filter,
                score_threshold=score_threshold,
            )

            return [
                {
                    "id": point.payload.get("_original_id", str(point.id)),
                    "score": point.score,
                    "payload": {k: v for k, v in (point.payload or {}).items() if k != "_original_id"},
                }
                for point in response.points
            ]
        except Exception as e:
            raise StorageError(f"Search failed: {e}") from e

    def delete_vectors(self, ids: list[str]) -> None:
        """Delete vectors by IDs.

        Args:
            ids: Vector IDs to delete (string IDs, converted to int internally)
        """
        int_ids = [_string_to_int_id(id_) for id_ in ids]
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=int_ids,
            )
            logger.debug(f"Deleted {len(ids)} vectors")
        except Exception as e:
            raise StorageError(f"Failed to delete vectors: {e}") from e

    def get_count(self) -> int:
        """Get total number of vectors in collection."""
        try:
            info = self.client.get_collection(self.collection_name)
            return info.points_count
        except Exception as e:
            raise StorageError(f"Failed to get count: {e}") from e

    def clear(self) -> None:
        """Clear all vectors from the collection."""
        try:
            self.client.delete_collection(self.collection_name)
            self._ensure_collection()
            logger.info(f"Cleared collection '{self.collection_name}'")
        except Exception as e:
            raise StorageError(f"Failed to clear collection: {e}") from e

    def close(self) -> None:
        """Close the client connection."""
        self.client.close()
