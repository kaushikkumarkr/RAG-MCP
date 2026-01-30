"""Configuration management for Nexus."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from nexus.exceptions import ConfigError


class EmbeddingConfig(BaseModel):
    """Configuration for embedding model."""

    model: str = Field(default="BAAI/bge-base-en-v1.5", description="Embedding model name")
    batch_size: int = Field(default=32, description="Batch size for embedding")
    normalize: bool = Field(default=True, description="Normalize embeddings")


class RerankerConfig(BaseModel):
    """Configuration for reranker model."""

    model: str = Field(default="BAAI/bge-reranker-base", description="Reranker model name")
    top_k: int = Field(default=5, description="Number of results after reranking")


class StorageConfig(BaseModel):
    """Configuration for storage backends."""

    vector_db: str = Field(default="embedded", description="Vector DB mode: embedded or server")
    qdrant_path: Path = Field(
        default=Path("~/.nexus/qdrant").expanduser(),
        description="Path for embedded Qdrant storage",
    )
    qdrant_url: str | None = Field(default=None, description="Qdrant server URL")
    metadata_db: Path = Field(
        default=Path("~/.nexus/metadata.db").expanduser(),
        description="Path for SQLite metadata database",
    )
    collection_name: str = Field(default="nexus_knowledge", description="Qdrant collection name")


class RetrievalConfig(BaseModel):
    """Configuration for retrieval settings."""

    top_k: int = Field(default=20, description="Initial retrieval count")
    rerank_top_k: int = Field(default=5, description="Results after reranking")
    use_reranking: bool = Field(default=True, description="Enable reranking")
    hybrid_alpha: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Weight for vector vs BM25 (1.0 = all vector)"
    )


class SourceConfig(BaseModel):
    """Configuration for a knowledge source."""

    path: Path = Field(description="Path to source directory or file")
    type: str = Field(default="markdown", description="Source type: markdown, pdf")
    watch: bool = Field(default=True, description="Watch for changes")
    recursive: bool = Field(default=True, description="Recursively index directories")


class ChunkingConfig(BaseModel):
    """Configuration for text chunking."""

    chunk_size: int = Field(default=512, description="Target chunk size in tokens")
    chunk_overlap: int = Field(default=50, description="Overlap between chunks")
    min_chunk_size: int = Field(default=100, description="Minimum chunk size")


class Config(BaseSettings):
    """Main configuration for Nexus."""

    model_config = SettingsConfigDict(
        env_prefix="NEXUS_",
        env_nested_delimiter="__",
    )

    # Component configs
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    reranker: RerankerConfig = Field(default_factory=RerankerConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)

    # Knowledge sources
    sources: list[SourceConfig] = Field(default_factory=list)

    # Notes storage directory
    notes_dir: Path = Field(
        default=Path("~/.nexus/notes").expanduser(),
        description="Directory for notes created via MCP",
    )

    # General data directory for memory/ingested content
    data_dir: Path = Field(
        default=Path("~/.nexus").expanduser(),
        description="Root directory for Nexus data",
    )


def load_config(config_path: Path | None = None) -> Config:
    """Load configuration from YAML file.

    Args:
        config_path: Path to config file. Defaults to ~/.nexus/config.yaml

    Returns:
        Loaded configuration

    Raises:
        ConfigError: If config file is invalid or missing required fields
    """
    if config_path is None:
        config_path = Path("~/.nexus/config.yaml").expanduser()

    if not config_path.exists():
        # Return default config if no file exists
        return Config()

    try:
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}
        return Config(**data)
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in config file {config_path}: {e}") from e
    except Exception as e:
        raise ConfigError(f"Failed to load config from {config_path}: {e}") from e


def save_config(config: Config, config_path: Path | None = None) -> None:
    """Save configuration to YAML file.

    Args:
        config: Configuration to save
        config_path: Path to save config. Defaults to ~/.nexus/config.yaml
    """
    if config_path is None:
        config_path = Path("~/.nexus/config.yaml").expanduser()

    config_path.parent.mkdir(parents=True, exist_ok=True)

    data = config.model_dump(mode="json")
    with open(config_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def create_default_config() -> Config:
    """Create a default configuration.

    Returns:
        Default configuration with sensible defaults
    """
    return Config()
