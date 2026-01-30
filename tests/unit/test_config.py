"""Tests for configuration module."""

import pytest
from pathlib import Path
import tempfile

from nexus.config import (
    Config,
    EmbeddingConfig,
    StorageConfig,
    load_config,
    save_config,
    create_default_config,
)
from nexus.exceptions import ConfigError


class TestConfig:
    """Tests for Config class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = create_default_config()
        
        assert config.embedding.model == "BAAI/bge-base-en-v1.5"
        assert config.embedding.batch_size == 32
        assert config.retrieval.top_k == 20
        assert config.retrieval.use_reranking is True
        assert config.storage.vector_db == "embedded"

    def test_custom_embedding_config(self):
        """Test custom embedding configuration."""
        config = Config(
            embedding=EmbeddingConfig(model="custom-model", batch_size=16)
        )
        assert config.embedding.model == "custom-model"
        assert config.embedding.batch_size == 16

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            
            # Create and save config
            config = create_default_config()
            config.embedding.batch_size = 64
            save_config(config, config_path)
            
            # Load and verify
            loaded = load_config(config_path)
            assert loaded.embedding.batch_size == 64
            assert loaded.embedding.model == config.embedding.model

    def test_load_missing_config_returns_default(self):
        """Test loading missing config file returns default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "nonexistent.yaml"
            config = load_config(config_path)
            
            # Should return default config
            assert config.embedding.model == "BAAI/bge-base-en-v1.5"

    def test_load_invalid_yaml_raises_error(self):
        """Test loading invalid YAML raises ConfigError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "invalid.yaml"
            config_path.write_text("{{invalid yaml}}")
            
            with pytest.raises(ConfigError):
                load_config(config_path)


class TestStorageConfig:
    """Tests for StorageConfig."""

    def test_default_paths(self):
        """Test default storage paths."""
        config = StorageConfig()
        
        assert config.vector_db == "embedded"
        assert config.collection_name == "nexus_knowledge"
