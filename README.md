# Nexus

**Personal Knowledge MCP Server** - A RAG-powered knowledge retrieval system for your personal notes and documents.

## Features

- 🔍 **Hybrid Search**: Combines semantic vector search with BM25 keyword matching
- 🧠 **Smart Embeddings**: Uses sentence-transformers for high-quality embeddings
- 📝 **Markdown Support**: Parse frontmatter, extract headings, and chunk intelligently
- 🔌 **MCP Integration**: Works as an MCP server for AI assistants
- ⚡ **Local-First**: All data stays on your machine with SQLite + Qdrant

## Quick Start

```bash
# Install
pip install -e .

# Initialize
nexus init

# Add a source
nexus add-source ~/Documents/notes

# Index your documents
nexus index

# Search
nexus search "machine learning concepts"

# Start MCP server
nexus serve
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `nexus init` | Initialize configuration |
| `nexus status` | Show knowledge base stats |
| `nexus add-source <path>` | Add a source directory |
| `nexus list-sources` | List configured sources |
| `nexus index [path]` | Index documents |
| `nexus search <query>` | Search knowledge base |
| `nexus serve` | Start MCP server |

## MCP Tools

When running as an MCP server, Nexus provides these tools:

- **search_knowledge**: Semantic + keyword search with filtering
- **list_sources**: View indexed sources
- **get_stats**: Knowledge base statistics
- **add_note**: Quick note creation and indexing

## Configuration

Configuration is stored at `~/.nexus/config.yaml`:

```yaml
embedding:
  model: BAAI/bge-base-en-v1.5
  batch_size: 32

storage:
  metadata_db: ~/.nexus/metadata.db
  qdrant_path: ~/.nexus/qdrant
  collection_name: nexus_knowledge

retrieval:
  top_k: 20
  hybrid_alpha: 0.5

chunking:
  chunk_size: 512
  chunk_overlap: 50
```

## Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint
ruff check src/
```

## Architecture

```
nexus/
├── cli/         # Typer CLI
├── config.py    # Pydantic configuration
├── ingest/      # Document loading, chunking, ingestion
├── models/      # Data models (Document, Chunk, Source)
├── rag/         # Embedder, Search, Hybrid search
├── storage/     # SQLite metadata + Qdrant vectors
└── tools/       # MCP server implementation
```

## License

MIT
