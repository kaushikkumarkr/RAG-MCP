"""Tests for markdown loader."""

import pytest
from pathlib import Path

from nexus.ingest.loader import MarkdownLoader


class TestMarkdownLoader:
    """Tests for MarkdownLoader class."""

    def test_parse_simple_content(self):
        """Test parsing simple markdown without frontmatter."""
        loader = MarkdownLoader()
        content = "# Hello World\n\nThis is some content."
        
        doc = loader.parse(content)
        
        assert "Hello World" in doc.content
        assert doc.title == "Hello World"
        assert len(doc.headings) == 1
        assert doc.headings[0] == (1, "Hello World", 1)

    def test_parse_frontmatter(self):
        """Test parsing markdown with frontmatter."""
        loader = MarkdownLoader()
        content = """---
title: My Document
tags: [python, testing]
author: Test Author
---

# Heading

Content here.
"""
        doc = loader.parse(content)
        
        assert doc.title == "My Document"
        assert "python" in doc.tags
        assert "testing" in doc.tags
        assert doc.author == "Test Author"
        assert "Heading" in doc.content

    def test_parse_multiple_headings(self):
        """Test extraction of multiple headings."""
        loader = MarkdownLoader()
        content = """# Main Title

## Section 1

Content 1

### Subsection 1.1

## Section 2

Content 2
"""
        doc = loader.parse(content)
        
        assert len(doc.headings) == 4
        assert doc.headings[0][1] == "Main Title"
        assert doc.headings[1][1] == "Section 1"
        assert doc.headings[2][1] == "Subsection 1.1"
        assert doc.headings[3][1] == "Section 2"

    def test_load_file(self, sample_markdown_file: Path):
        """Test loading a markdown file."""
        loader = MarkdownLoader()
        
        doc = loader.load_file(sample_markdown_file)
        
        assert doc.title == "Test Document"
        assert "python" in doc.tags
        assert "machine learning" in doc.content

    def test_load_directory(self, temp_dir: Path):
        """Test loading all files from a directory."""
        loader = MarkdownLoader()
        
        # Create test files
        (temp_dir / "file1.md").write_text("# File 1\n\nContent 1")
        (temp_dir / "file2.md").write_text("# File 2\n\nContent 2")
        (temp_dir / "subdir").mkdir()
        (temp_dir / "subdir" / "file3.md").write_text("# File 3\n\nContent 3")
        
        # Non-recursive
        results = loader.load_directory(temp_dir, recursive=False)
        assert len(results) == 2
        
        # Recursive
        results = loader.load_directory(temp_dir, recursive=True)
        assert len(results) == 3

    def test_parse_date_in_frontmatter(self):
        """Test parsing date from frontmatter."""
        loader = MarkdownLoader()
        content = """---
title: Dated Doc
date: 2024-01-15
---

Content
"""
        doc = loader.parse(content)
        
        assert doc.created_at is not None
        assert doc.created_at.year == 2024
        assert doc.created_at.month == 1
        assert doc.created_at.day == 15

    def test_tags_as_string(self):
        """Test parsing tags as comma-separated string."""
        loader = MarkdownLoader()
        content = """---
tags: python, testing, markdown
---

Content
"""
        doc = loader.parse(content)
        
        assert len(doc.tags) == 3
        assert "python" in doc.tags
