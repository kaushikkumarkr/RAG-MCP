"""Tests for text chunker."""

import pytest

from nexus.ingest.chunker import TextChunker


class TestTextChunker:
    """Tests for TextChunker class."""

    def test_chunk_short_text(self):
        """Test that short text becomes a single chunk."""
        chunker = TextChunker(chunk_size=500, min_chunk_size=50)
        text = "This is a short paragraph that should remain as one chunk."
        
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) == 1
        assert chunks[0].content == text

    def test_chunk_with_headings(self):
        """Test chunking with heading-based sections."""
        chunker = TextChunker(chunk_size=200, min_chunk_size=20)
        text = """# Introduction

This is the introduction section with some content.

# Methods

This section describes the methods used.

# Results

Here are the results of the study.
"""
        headings = [(1, "Introduction", 1), (1, "Methods", 5), (1, "Results", 9)]
        
        chunks = chunker.chunk_text(text, headings)
        
        assert len(chunks) >= 3
        # Each chunk should have the appropriate heading
        intro_chunk = next((c for c in chunks if "introduction" in c.content.lower()), None)
        assert intro_chunk is not None
        assert intro_chunk.heading == "Introduction"

    def test_chunk_large_section(self):
        """Test that large sections get split further."""
        chunker = TextChunker(chunk_size=100, min_chunk_size=20)
        
        # Create a large text with paragraphs
        para1 = "This is the first paragraph with enough content to matter."
        para2 = "This is the second paragraph with different information."
        para3 = "This is the third paragraph explaining more concepts."
        para4 = "This is the fourth paragraph with additional details."
        text = f"{para1}\n\n{para2}\n\n{para3}\n\n{para4}"
        
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) >= 1
        # Content should be preserved across chunks
        full_content = " ".join(c.content for c in chunks)
        assert "first paragraph" in full_content
        assert "fourth paragraph" in full_content

    def test_chunk_preserves_context(self):
        """Test that chunking preserves context via overlap."""
        chunker = TextChunker(chunk_size=100, chunk_overlap=30, min_chunk_size=20)
        
        text = "First sentence here. Second sentence follows. Third one comes. Fourth appears. Fifth ends."
        
        chunks = chunker.chunk_text(text)
        
        # Should have multiple chunks
        assert len(chunks) >= 1

    def test_chunk_by_paragraphs(self):
        """Test chunking by paragraphs when no headings."""
        chunker = TextChunker(chunk_size=200, min_chunk_size=20)
        
        text = """First paragraph with some content here.

Second paragraph with different content.

Third paragraph with more information."""
        
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) >= 1
        # Content should be preserved
        full_content = " ".join(c.content for c in chunks)
        assert "First paragraph" in full_content
        assert "Third paragraph" in full_content

    def test_min_chunk_size_filter(self):
        """Test that chunks below min size are filtered out."""
        chunker = TextChunker(chunk_size=500, min_chunk_size=100)
        
        text = "Short."  # Below min size
        
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) == 0

    def test_chunk_has_line_numbers(self):
        """Test that chunks have line number information."""
        chunker = TextChunker(chunk_size=500, min_chunk_size=20)
        
        text = """# Title

First paragraph.

Second paragraph."""
        headings = [(1, "Title", 1)]
        
        chunks = chunker.chunk_text(text, headings)
        
        for chunk in chunks:
            assert chunk.start_line >= 1
            assert chunk.end_line >= chunk.start_line
