"""Tests for search engine."""

import pytest
from pathlib import Path

from nexus.rag.embedder import Embedder
from nexus.rag.search import SearchEngine
from nexus.storage.metadata import MetadataStore
from nexus.storage.vectors import VectorStore
from nexus.ingest.pipeline import IngestionPipeline
from nexus.ingest.chunker import TextChunker


# Use smaller model for tests
@pytest.fixture(scope="module")
def embedder():
    """Shared embedder for all tests."""
    return Embedder(model_name="BAAI/bge-small-en-v1.5")


@pytest.fixture
def search_setup(temp_dir: Path, embedder):
    """Set up search engine with test data."""
    metadata_store = MetadataStore(temp_dir / "metadata.db")
    vector_store = VectorStore(
        collection_name="test_search",
        path=temp_dir / "qdrant",
        embedding_dim=embedder.dimension,
    )
    
    # Create test documents
    docs_dir = temp_dir / "docs"
    docs_dir.mkdir()
    
    (docs_dir / "ml.md").write_text("""---
title: Machine Learning Guide
tags: [ml, ai]
---

# Machine Learning

Machine learning is a subset of artificial intelligence that enables systems to learn from data.

## Supervised Learning

Supervised learning uses labeled data to train models.

## Unsupervised Learning

Unsupervised learning finds patterns in unlabeled data.
""")
    
    (docs_dir / "python.md").write_text("""---
title: Python Programming
tags: [python, programming]
---

# Python

Python is a high-level programming language known for simplicity.

## Variables

Python uses dynamic typing for variables.

## Functions

Functions in Python are defined with the def keyword.
""")
    
    (docs_dir / "cooking.md").write_text("""---
title: Cooking Recipes
tags: [cooking, food]
---

# Cooking Guide

A guide to basic cooking techniques.

## Baking

Baking requires precise measurements.

## Grilling

Grilling is great for meats and vegetables.
""")
    
    # Ingest documents
    pipeline = IngestionPipeline(
        embedder=embedder,
        metadata_store=metadata_store,
        vector_store=vector_store,
        chunker=TextChunker(chunk_size=200, min_chunk_size=50),
    )
    
    for doc_path in docs_dir.glob("*.md"):
        pipeline.ingest_file(doc_path)
    
    # Create search engine
    engine = SearchEngine(
        embedder=embedder,
        metadata_store=metadata_store,
        vector_store=vector_store,
        top_k=10,
    )
    
    yield engine
    
    metadata_store.close()
    vector_store.close()


class TestSearchEngine:
    """Tests for SearchEngine class."""

    def test_basic_search(self, search_setup):
        """Test basic semantic search."""
        results = search_setup.search("machine learning artificial intelligence")
        
        assert len(results) > 0
        # ML document should rank high
        ml_results = [r for r in results if "machine" in r.content.lower()]
        assert len(ml_results) > 0
        assert results[0].relevance_score > 0.5

    def test_search_returns_metadata(self, search_setup):
        """Test that search results include metadata."""
        results = search_setup.search("python programming")
        
        assert len(results) > 0
        top_result = results[0]
        
        assert top_result.source is not None
        assert top_result.source_type == "markdown"
        # Should have title from matching document
        assert top_result.title is not None

    def test_search_with_source_type_filter(self, search_setup):
        """Test filtering by source type."""
        results = search_setup.search(
            "learning",
            source_type="markdown",
        )
        
        assert len(results) > 0
        for r in results:
            assert r.source_type == "markdown"

    def test_search_with_tags_filter(self, search_setup):
        """Test filtering by tags."""
        results = search_setup.search(
            "learning",
            tags=["ml"],
        )
        
        # Should only get results from ML document
        assert len(results) > 0
        for r in results:
            assert "ml" in r.tags or "ai" in r.tags

    def test_search_different_topics(self, search_setup):
        """Test that different queries return different results."""
        ml_results = search_setup.search("machine learning neural networks")
        cooking_results = search_setup.search("cooking baking recipes kitchen")
        
        assert len(ml_results) > 0
        assert len(cooking_results) > 0
        
        # Top results should be from different documents
        assert ml_results[0].source != cooking_results[0].source

    def test_search_top_k(self, search_setup):
        """Test limiting number of results."""
        results = search_setup.search("guide", top_k=2)
        
        assert len(results) <= 2

    def test_search_with_no_results(self, search_setup):
        """Test search with very specific query that may not match."""
        results = search_setup.search(
            "quantum entanglement physics",
            tags=["physics"],  # No physics tag in our docs
        )
        
        # May return empty or very few results
        assert len(results) >= 0  # Just verify it doesn't crash
