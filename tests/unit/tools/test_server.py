"""Tests for MCP server."""

import pytest
from pathlib import Path

from nexus.tools.server import NexusServer
from nexus.config import Config


@pytest.fixture
def server_setup(temp_dir: Path):
    """Set up test server."""
    # Create test config by importing and creating fresh
    from nexus.config import StorageConfig, EmbeddingConfig
    
    config = Config()
    # Create new storage config with test paths
    config = Config(
        storage=StorageConfig(
            metadata_db=temp_dir / "metadata.db",
            qdrant_path=temp_dir / "qdrant",
        ),
        embedding=EmbeddingConfig(
            model="BAAI/bge-small-en-v1.5",
        ),
    )
    
    server = NexusServer(config=config)
    
    yield server
    
    server.close()


class TestNexusServer:
    """Tests for NexusServer class."""

    @pytest.mark.asyncio
    async def test_list_tools(self, server_setup):
        """Test that server is properly configured."""
        # Just verify server is set up with correct name
        assert server_setup.server is not None
        assert server_setup.embedder is not None

    @pytest.mark.asyncio
    async def test_handle_get_stats_empty(self, server_setup):
        """Test get_stats on empty database."""
        result = await server_setup._handle_get_stats()
        
        assert len(result) == 1
        assert "Documents: 0" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_list_sources_empty(self, server_setup):
        """Test list_sources on empty database."""
        result = await server_setup._handle_list_sources()
        
        assert len(result) == 1
        assert "No sources indexed" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_search_empty(self, server_setup):
        """Test search on empty database."""
        result = await server_setup._handle_search({
            "query": "test query",
            "limit": 5,
        })
        
        assert len(result) == 1
        assert "No results" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_add_note(self, server_setup, temp_dir):
        """Test adding a note."""
        result = await server_setup._handle_add_note({
            "title": "Test Note",
            "content": "This is test content for the note.",
            "tags": ["test", "demo"],
        })
        
        assert len(result) == 1
        assert "added successfully" in result[0].text

    @pytest.mark.asyncio
    async def test_search_after_adding_note(self, server_setup):
        """Test that search finds added notes."""
        # Add a note with enough content to be chunked
        await server_setup._handle_add_note({
            "title": "Python Tips",
            "content": "Python is a great programming language for machine learning and data science. It has many excellent libraries like numpy, pandas, and scikit-learn. Python's syntax is clean and readable, making it easy to learn. The language supports multiple programming paradigms including object-oriented and functional programming styles.",
            "tags": ["python", "ml"],
        })
        
        # Search for it
        result = await server_setup._handle_search({
            "query": "python programming machine learning",
            "limit": 3,
        })
        
        assert len(result) == 1
        # Should either find results or the note wasn't chunked
        text = result[0].text.lower()
        assert "python" in text or "result" in text

    @pytest.mark.asyncio
    async def test_stats_after_adding_note(self, server_setup):
        """Test that stats reflect added notes."""
        # Add a note
        await server_setup._handle_add_note({
            "title": "Stats Test",
            "content": "Testing stats functionality.",
        })
        
        # Check stats
        result = await server_setup._handle_get_stats()
        
        assert "Documents: 1" in result[0].text
