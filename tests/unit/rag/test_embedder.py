"""Tests for embedder."""

import pytest

from nexus.rag.embedder import Embedder


# Mark these tests as slow since they load the model
pytestmark = pytest.mark.slow


class TestEmbedder:
    """Tests for Embedder class."""

    @pytest.fixture(scope="class")
    def embedder(self):
        """Create embedder instance (shared across tests)."""
        # Use a smaller model for faster tests
        return Embedder(model_name="BAAI/bge-small-en-v1.5")

    def test_embed_text(self, embedder):
        """Test embedding a single text."""
        text = "This is a test document about machine learning."
        
        embedding = embedder.embed_text(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == embedder.dimension
        # Normalized embedding should have magnitude ~1
        magnitude = sum(x**2 for x in embedding) ** 0.5
        assert abs(magnitude - 1.0) < 0.01

    def test_embed_texts(self, embedder):
        """Test embedding multiple texts."""
        texts = [
            "First document about Python.",
            "Second document about JavaScript.",
            "Third document about Rust.",
        ]
        
        embeddings = embedder.embed_texts(texts)
        
        assert len(embeddings) == 3
        assert all(len(e) == embedder.dimension for e in embeddings)

    def test_embed_empty_list(self, embedder):
        """Test embedding empty list returns empty list."""
        embeddings = embedder.embed_texts([])
        assert embeddings == []

    def test_similarity(self, embedder):
        """Test similarity between texts."""
        text1 = "Machine learning is a subset of artificial intelligence."
        text2 = "AI includes machine learning as one of its branches."
        text3 = "The weather today is sunny and warm."
        
        # Similar texts should have higher similarity
        sim_related = embedder.similarity(text1, text2)
        sim_unrelated = embedder.similarity(text1, text3)
        
        assert sim_related > sim_unrelated
        assert sim_related > 0.5  # Related texts should be > 0.5

    def test_embedding_dimension(self, embedder):
        """Test that dimension property works."""
        assert embedder.dimension > 0
        assert embedder.dimension == 384  # bge-small dimension
