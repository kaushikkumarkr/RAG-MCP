"""Tests for BM25 and hybrid search."""

import pytest
from pathlib import Path

from nexus.rag.bm25 import BM25Index, tokenize
from nexus.rag.hybrid import HybridSearchEngine, reciprocal_rank_fusion
from nexus.rag.embedder import Embedder
from nexus.storage.metadata import MetadataStore
from nexus.storage.vectors import VectorStore
from nexus.ingest.pipeline import IngestionPipeline
from nexus.ingest.chunker import TextChunker


class TestTokenize:
    """Tests for tokenize function."""

    def test_basic_tokenize(self):
        """Test basic tokenization."""
        tokens = tokenize("Hello World! This is a test.")
        assert tokens == ["hello", "world", "this", "is", "a", "test"]

    def test_tokenize_with_numbers(self):
        """Test tokenization with numbers."""
        tokens = tokenize("Python 3.11 is great")
        assert "python" in tokens
        assert "3" in tokens
        assert "11" in tokens


class TestRRF:
    """Tests for reciprocal rank fusion."""

    def test_rrf_single_list(self):
        """Test RRF with single list."""
        results = [[("a", 1.0), ("b", 0.9), ("c", 0.8)]]
        fused = reciprocal_rank_fusion(results)
        
        # Order should be preserved
        assert fused[0][0] == "a"
        assert fused[1][0] == "b"
        assert fused[2][0] == "c"

    def test_rrf_fusion(self):
        """Test RRF combining two lists."""
        list1 = [("a", 1.0), ("b", 0.9), ("c", 0.8)]
        list2 = [("c", 1.0), ("a", 0.9), ("d", 0.8)]
        
        fused = reciprocal_rank_fusion([list1, list2])
        ids = [doc_id for doc_id, _ in fused]
        
        # Both a and c should be near top (appear in both lists)
        assert "a" in ids[:3]
        assert "c" in ids[:3]

    def test_rrf_gives_boost_to_both_matches(self):
        """Test that items in both lists get boosted."""
        list1 = [("x", 1.0), ("y", 0.9)]
        list2 = [("y", 1.0), ("z", 0.9)]
        
        fused = reciprocal_rank_fusion([list1, list2])
        
        # y should be first because it appears in both lists
        assert fused[0][0] == "y"


# Use smaller model for tests
@pytest.fixture(scope="module")
def embedder():
    """Shared embedder for all tests."""
    return Embedder(model_name="BAAI/bge-small-en-v1.5")


@pytest.fixture
def hybrid_setup(temp_dir: Path, embedder):
    """Set up hybrid search engine with test data."""
    metadata_store = MetadataStore(temp_dir / "metadata.db")
    vector_store = VectorStore(
        collection_name="test_hybrid",
        path=temp_dir / "qdrant",
        embedding_dim=embedder.dimension,
    )
    
    # Create test documents
    docs_dir = temp_dir / "docs"
    docs_dir.mkdir()
    
    (docs_dir / "ml.md").write_text("""---
title: Machine Learning
tags: [ml]
---

# Machine Learning

Deep learning neural networks are used for AI tasks.
Supervised learning requires labeled training data.
""")
    
    (docs_dir / "cooking.md").write_text("""---
title: Cooking Guide
tags: [cooking]
---

# Cooking

Baking bread requires flour and yeast.
Grilling vegetables is a healthy cooking method.
""")
    
    # Ingest
    pipeline = IngestionPipeline(
        embedder=embedder,
        metadata_store=metadata_store,
        vector_store=vector_store,
        chunker=TextChunker(chunk_size=150, min_chunk_size=30),
    )
    
    for doc_path in docs_dir.glob("*.md"):
        pipeline.ingest_file(doc_path)
    
    # Create BM25 index
    bm25_index = BM25Index(metadata_store)
    bm25_index.build_index()
    
    # Create hybrid engine
    engine = HybridSearchEngine(
        embedder=embedder,
        metadata_store=metadata_store,
        vector_store=vector_store,
        bm25_index=bm25_index,
        top_k=10,
    )
    
    yield engine
    
    metadata_store.close()
    vector_store.close()


class TestHybridSearch:
    """Tests for HybridSearchEngine class."""

    def test_hybrid_search(self, hybrid_setup):
        """Test hybrid search returns results."""
        results = hybrid_setup.search("machine learning neural networks")
        
        assert len(results) > 0
        # ML content should be relevant
        top_content = " ".join(r.content.lower() for r in results[:2])
        assert "learning" in top_content or "neural" in top_content

    def test_vector_only_search(self, hybrid_setup):
        """Test vector-only search (no hybrid)."""
        results = hybrid_setup.search("cooking recipes", use_hybrid=False)
        
        assert len(results) > 0

    def test_hybrid_uses_both_methods(self, hybrid_setup):
        """Test that hybrid combines vector and BM25."""
        # A query that might get different results from vector vs keyword
        hybrid_results = hybrid_setup.search("flour bread baking")
        vector_results = hybrid_setup.search("flour bread baking", use_hybrid=False)
        
        # Both should return results
        assert len(hybrid_results) > 0
        assert len(vector_results) > 0

    def test_search_with_reranking(self, hybrid_setup):
        """Test search with reranking enabled."""
        hybrid_setup.use_reranking = True
        hybrid_setup.rerank_top_k = 2
        
        results = hybrid_setup.search("machine learning")
        
        # Should have at most rerank_top_k results
        assert len(results) <= 2
        
        hybrid_setup.use_reranking = False
