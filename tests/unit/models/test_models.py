"""Tests for data models."""

import pytest
from datetime import datetime

from nexus.models.document import Document, Chunk, ChunkMetadata
from nexus.models.source import Source, SourceType


class TestChunkMetadata:
    """Tests for ChunkMetadata model."""

    def test_minimal_metadata(self):
        """Test creating metadata with minimal fields."""
        metadata = ChunkMetadata(
            source_path="/path/to/file.md",
            source_type="markdown",
        )
        assert metadata.source_path == "/path/to/file.md"
        assert metadata.tags == []
        assert metadata.title is None

    def test_full_metadata(self):
        """Test creating metadata with all fields."""
        metadata = ChunkMetadata(
            source_path="/path/to/file.md",
            source_type="markdown",
            start_line=10,
            end_line=20,
            heading="Test Section",
            tags=["python", "testing"],
            title="Test Doc",
        )
        assert metadata.heading == "Test Section"
        assert "python" in metadata.tags


class TestChunk:
    """Tests for Chunk model."""

    def test_create_chunk(self):
        """Test creating a chunk."""
        metadata = ChunkMetadata(
            source_path="/test.md",
            source_type="markdown",
        )
        chunk = Chunk(
            id="chunk-1",
            content="Test content",
            document_id="doc-1",
            metadata=metadata,
        )
        assert chunk.id == "chunk-1"
        assert chunk.embedding is None

    def test_chunk_with_embedding(self):
        """Test chunk with embedding vector."""
        metadata = ChunkMetadata(
            source_path="/test.md",
            source_type="markdown",
        )
        chunk = Chunk(
            id="chunk-1",
            content="Test content",
            document_id="doc-1",
            metadata=metadata,
            embedding=[0.1, 0.2, 0.3],
        )
        assert len(chunk.embedding) == 3


class TestDocument:
    """Tests for Document model."""

    def test_create_document(self):
        """Test creating a document."""
        doc = Document(
            id="doc-1",
            source_path="/path/to/file.md",
            source_type="markdown",
            content="Full content here",
        )
        assert doc.id == "doc-1"
        assert doc.chunks == []
        assert doc.indexed_at is not None


class TestSource:
    """Tests for Source model."""

    def test_create_source(self):
        """Test creating a source."""
        source = Source(
            id="src-1",
            path="/path/to/vault",
            source_type=SourceType.MARKDOWN,
        )
        assert source.document_count == 0
        assert source.source_type == SourceType.MARKDOWN

    def test_source_types(self):
        """Test all source types."""
        assert SourceType.MARKDOWN.value == "markdown"
        assert SourceType.PDF.value == "pdf"
        assert SourceType.NOTE.value == "note"
