"""Pytest configuration and shared fixtures."""

import pytest
from pathlib import Path
import tempfile

from nexus.config import Config, StorageConfig


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_config(temp_dir: Path) -> Config:
    """Test configuration with temporary storage paths."""
    return Config(
        storage=StorageConfig(
            vector_db="embedded",
            qdrant_path=temp_dir / "qdrant",
            metadata_db=temp_dir / "metadata.db",
        )
    )


@pytest.fixture
def sample_markdown_content() -> str:
    """Sample markdown content for testing."""
    return '''---
title: Test Document
tags: [python, testing]
---

# Heading 1

This is a test document with some content about machine learning.

## Subheading

Here is more content about neural networks and deep learning.

```python
def hello():
    print("Hello, World!")
```

### Another Section

Final thoughts on artificial intelligence.
'''


@pytest.fixture
def sample_markdown_file(temp_dir: Path, sample_markdown_content: str) -> Path:
    """Create a sample markdown file for testing."""
    md_file = temp_dir / "test.md"
    md_file.write_text(sample_markdown_content)
    return md_file
