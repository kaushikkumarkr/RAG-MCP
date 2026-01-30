"""Tests for vector storage."""

import pytest
from pathlib import Path

from nexus.storage.vectors import VectorStore
from nexus.exceptions import StorageError


class TestVectorStore:
    """Tests for VectorStore class."""

    def test_init_creates_collection(self, temp_dir: Path):
        """Test that initialization creates the collection."""
        store = VectorStore(
            collection_name="test_collection",
            path=temp_dir / "qdrant",
            embedding_dim=384,
        )
        
        assert store.get_count() == 0
        store.close()

    def test_add_and_search_vectors(self, temp_dir: Path):
        """Test adding and searching vectors."""
        store = VectorStore(
            collection_name="test_collection",
            path=temp_dir / "qdrant",
            embedding_dim=4,  # Small dimension for testing
        )
        
        # Add vectors
        ids = ["v1", "v2", "v3"]
        vectors = [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.9, 0.1, 0.0, 0.0],  # Similar to v1
        ]
        payloads = [
            {"source": "doc1"},
            {"source": "doc2"},
            {"source": "doc1"},
        ]
        
        store.add_vectors(ids, vectors, payloads)
        assert store.get_count() == 3
        
        # Search with query similar to v1
        query = [1.0, 0.0, 0.0, 0.0]
        results = store.search(query, limit=2)
        
        assert len(results) == 2
        # v1 should be most similar (exact match)
        assert results[0]["id"] == "v1"
        assert results[0]["score"] > 0.9
        
        store.close()

    def test_search_with_filters(self, temp_dir: Path):
        """Test searching with metadata filters."""
        store = VectorStore(
            collection_name="test_collection",
            path=temp_dir / "qdrant",
            embedding_dim=4,
        )
        
        ids = ["v1", "v2", "v3"]
        vectors = [
            [1.0, 0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0, 0.0],
        ]
        payloads = [
            {"source_type": "markdown"},
            {"source_type": "pdf"},
            {"source_type": "markdown"},
        ]
        
        store.add_vectors(ids, vectors, payloads)
        
        # Search with filter
        results = store.search(
            query_vector=[1.0, 0.0, 0.0, 0.0],
            limit=10,
            filters={"source_type": "markdown"},
        )
        
        assert len(results) == 2
        for r in results:
            assert r["payload"]["source_type"] == "markdown"
        
        store.close()

    def test_delete_vectors(self, temp_dir: Path):
        """Test deleting vectors."""
        store = VectorStore(
            collection_name="test_collection",
            path=temp_dir / "qdrant",
            embedding_dim=4,
        )
        
        store.add_vectors(
            ids=["v1", "v2"],
            vectors=[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]],
        )
        
        assert store.get_count() == 2
        
        store.delete_vectors(["v1"])
        assert store.get_count() == 1
        
        store.close()

    def test_clear_collection(self, temp_dir: Path):
        """Test clearing all vectors."""
        store = VectorStore(
            collection_name="test_collection",
            path=temp_dir / "qdrant",
            embedding_dim=4,
        )
        
        store.add_vectors(
            ids=["v1", "v2", "v3"],
            vectors=[
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
            ],
        )
        
        assert store.get_count() == 3
        
        store.clear()
        assert store.get_count() == 0
        
        store.close()

    def test_add_vectors_validates_length(self, temp_dir: Path):
        """Test that mismatched lengths raise error."""
        store = VectorStore(
            collection_name="test_collection",
            path=temp_dir / "qdrant",
            embedding_dim=4,
        )
        
        with pytest.raises(StorageError):
            store.add_vectors(
                ids=["v1", "v2"],
                vectors=[[1.0, 0.0, 0.0, 0.0]],  # Only one vector
            )
        
        store.close()
