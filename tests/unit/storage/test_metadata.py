"""Tests for metadata storage."""

import pytest
from pathlib import Path

from nexus.storage.metadata import MetadataStore
from nexus.models.document import Document, Chunk, ChunkMetadata
from nexus.models.source import Source, SourceType


class TestMetadataStore:
    """Tests for MetadataStore class."""

    def test_init_creates_database(self, temp_dir: Path):
        """Test that initialization creates the database."""
        db_path = temp_dir / "test.db"
        store = MetadataStore(db_path)
        
        assert db_path.exists()
        store.close()

    def test_add_and_get_source(self, temp_dir: Path):
        """Test adding and retrieving a source."""
        store = MetadataStore(temp_dir / "test.db")
        
        source = Source(
            id="src-1",
            path="/path/to/vault",
            source_type=SourceType.MARKDOWN,
            title="My Vault",
        )
        
        store.add_source(source)
        retrieved = store.get_source("src-1")
        
        assert retrieved is not None
        assert retrieved.id == "src-1"
        assert retrieved.path == "/path/to/vault"
        assert retrieved.source_type == SourceType.MARKDOWN
        
        store.close()

    def test_list_sources(self, temp_dir: Path):
        """Test listing all sources."""
        store = MetadataStore(temp_dir / "test.db")
        
        store.add_source(Source(id="s1", path="/p1", source_type=SourceType.MARKDOWN))
        store.add_source(Source(id="s2", path="/p2", source_type=SourceType.PDF))
        
        sources = store.list_sources()
        assert len(sources) == 2
        
        store.close()

    def test_add_and_get_document(self, temp_dir: Path):
        """Test adding and retrieving a document."""
        store = MetadataStore(temp_dir / "test.db")
        
        doc = Document(
            id="doc-1",
            source_path="/test.md",
            source_type="markdown",
            title="Test Document",
            content="Full content here",
            content_hash="abc123",
        )
        
        store.add_document(doc)
        retrieved = store.get_document("doc-1")
        
        assert retrieved is not None
        assert retrieved.id == "doc-1"
        assert retrieved.title == "Test Document"
        assert retrieved.content_hash == "abc123"
        
        store.close()

    def test_document_exists(self, temp_dir: Path):
        """Test document existence check."""
        store = MetadataStore(temp_dir / "test.db")
        
        doc = Document(
            id="doc-1",
            source_path="/test.md",
            source_type="markdown",
            content="Content",
            content_hash="hash123",
        )
        store.add_document(doc)
        
        assert store.document_exists("/test.md", "hash123") is True
        assert store.document_exists("/test.md", "different") is False
        assert store.document_exists("/other.md", "hash123") is False
        
        store.close()

    def test_add_and_get_chunk(self, temp_dir: Path):
        """Test adding and retrieving a chunk."""
        store = MetadataStore(temp_dir / "test.db")
        
        # First add a document
        doc = Document(
            id="doc-1",
            source_path="/test.md",
            source_type="markdown",
            content="Full content",
        )
        store.add_document(doc)
        
        # Add a chunk
        chunk = Chunk(
            id="chunk-1",
            document_id="doc-1",
            content="Chunk content about machine learning",
            chunk_index=0,
            metadata=ChunkMetadata(
                source_path="/test.md",
                source_type="markdown",
                heading="Introduction",
                tags=["python", "ml"],
            ),
        )
        store.add_chunk(chunk)
        
        # Retrieve and verify
        retrieved = store.get_chunk("chunk-1")
        assert retrieved is not None
        assert retrieved.content == "Chunk content about machine learning"
        assert retrieved.metadata.heading == "Introduction"
        assert "python" in retrieved.metadata.tags
        
        store.close()

    def test_get_chunks_by_document(self, temp_dir: Path):
        """Test getting all chunks for a document."""
        store = MetadataStore(temp_dir / "test.db")
        
        doc = Document(
            id="doc-1",
            source_path="/test.md",
            source_type="markdown",
            content="Full content",
        )
        store.add_document(doc)
        
        for i in range(3):
            chunk = Chunk(
                id=f"chunk-{i}",
                document_id="doc-1",
                content=f"Content {i}",
                chunk_index=i,
                metadata=ChunkMetadata(
                    source_path="/test.md",
                    source_type="markdown",
                ),
            )
            store.add_chunk(chunk)
        
        chunks = store.get_chunks_by_document("doc-1")
        assert len(chunks) == 3
        assert chunks[0].chunk_index == 0
        assert chunks[2].chunk_index == 2
        
        store.close()

    def test_get_chunks_by_ids(self, temp_dir: Path):
        """Test getting chunks by list of IDs."""
        store = MetadataStore(temp_dir / "test.db")
        
        doc = Document(
            id="doc-1",
            source_path="/test.md",
            source_type="markdown",
            content="Content",
        )
        store.add_document(doc)
        
        for i in range(5):
            chunk = Chunk(
                id=f"chunk-{i}",
                document_id="doc-1",
                content=f"Content {i}",
                chunk_index=i,
                metadata=ChunkMetadata(
                    source_path="/test.md",
                    source_type="markdown",
                ),
            )
            store.add_chunk(chunk)
        
        chunks = store.get_chunks_by_ids(["chunk-1", "chunk-3"])
        assert len(chunks) == 2
        
        store.close()

    def test_delete_document(self, temp_dir: Path):
        """Test deleting a document and its chunks."""
        store = MetadataStore(temp_dir / "test.db")
        
        doc = Document(
            id="doc-1",
            source_path="/test.md",
            source_type="markdown",
            content="Content",
        )
        store.add_document(doc)
        
        chunk = Chunk(
            id="chunk-1",
            document_id="doc-1",
            content="Chunk content",
            chunk_index=0,
            metadata=ChunkMetadata(
                source_path="/test.md",
                source_type="markdown",
            ),
        )
        store.add_chunk(chunk)
        
        # Delete document
        store.delete_document("doc-1")
        
        assert store.get_document("doc-1") is None
        assert store.get_chunk("chunk-1") is None
        
        store.close()

    def test_get_stats(self, temp_dir: Path):
        """Test getting database statistics."""
        store = MetadataStore(temp_dir / "test.db")
        
        # Add some data
        store.add_source(Source(id="s1", path="/p1", source_type=SourceType.MARKDOWN))
        
        doc = Document(
            id="doc-1",
            source_path="/test.md",
            source_type="markdown",
            content="Content",
        )
        store.add_document(doc)
        
        chunk = Chunk(
            id="chunk-1",
            document_id="doc-1",
            content="Chunk",
            chunk_index=0,
            metadata=ChunkMetadata(source_path="/test.md", source_type="markdown"),
        )
        store.add_chunk(chunk)
        
        stats = store.get_stats()
        assert stats["sources"] == 1
        assert stats["documents"] == 1
        assert stats["chunks"] == 1
        
        store.close()
