# Nexus: AI Agent Guidelines & Coding Standards
## AGENTS.md

**Version:** 1.0  
**Last Updated:** January 2025  
**Purpose:** Guide AI agents and developers on how to make decisions and write code for this project

---

## Table of Contents

1. [Project Identity](#1-project-identity)
2. [Architecture Principles](#2-architecture-principles)
3. [Technology Stack](#3-technology-stack)
4. [Project Structure](#4-project-structure)
5. [Coding Standards](#5-coding-standards)
6. [Naming Conventions](#6-naming-conventions)
7. [Error Handling](#7-error-handling)
8. [Testing Standards](#8-testing-standards)
9. [Documentation Standards](#9-documentation-standards)
10. [Git Workflow](#10-git-workflow)
11. [Decision Framework](#11-decision-framework)
12. [Anti-Patterns to Avoid](#12-anti-patterns-to-avoid)
13. [Performance Guidelines](#13-performance-guidelines)
14. [Security Guidelines](#14-security-guidelines)

---

## 1. Project Identity

### What Nexus Is

- **An MCP Server** — Exposes tools via Model Context Protocol
- **A RAG Engine** — Provides intelligent retrieval over personal knowledge
- **Local-First** — All processing happens on user's machine
- **Open Source** — MIT licensed, community-driven

### What Nexus Is NOT

- ❌ A chat application (MCP clients provide UI)
- ❌ An LLM wrapper (MCP clients handle generation)
- ❌ A note-taking app (integrates with existing apps)
- ❌ A cloud service (no external dependencies required)
- ❌ An enterprise solution (focused on individual users)

### Core Values

| Value | Meaning | Implication |
|-------|---------|-------------|
| **Simplicity** | Easy to understand and use | Prefer simple solutions over clever ones |
| **Privacy** | User data never leaves their machine | No telemetry, no cloud dependencies |
| **Quality** | Production-grade, not a toy | Proper error handling, testing, docs |
| **Openness** | Transparent and extensible | Clear code, plugin architecture |

---

## 2. Architecture Principles

### Principle 1: Separation of Concerns

```
┌─────────────────────────────────────────────────────────┐
│                    MCP INTERFACE                         │
│           (Only knows about tools and responses)         │
├─────────────────────────────────────────────────────────┤
│                    SERVICE LAYER                         │
│        (Orchestrates operations, business logic)         │
├─────────────────────────────────────────────────────────┤
│                      RAG LAYER                           │
│    (Retrieval logic, ranking, query processing)         │
├─────────────────────────────────────────────────────────┤
│                   STORAGE LAYER                          │
│        (Vector DB, metadata DB, abstractions)           │
├─────────────────────────────────────────────────────────┤
│                   INGESTION LAYER                        │
│      (Parsers, chunkers, embedders, watchers)           │
└─────────────────────────────────────────────────────────┘
```

**Rule:** Each layer only talks to the layer directly below it. No skipping layers.

### Principle 2: Dependency Injection

Components should receive their dependencies, not create them.

**Good:**
```python
class Retriever:
    def __init__(self, vector_store: VectorStore, embedder: Embedder):
        self.vector_store = vector_store
        self.embedder = embedder
```

**Bad:**
```python
class Retriever:
    def __init__(self):
        self.vector_store = QdrantStore()  # Hard-coded dependency
        self.embedder = BGEEmbedder()      # Hard-coded dependency
```

### Principle 3: Configuration Over Code

Behavior should be configurable without code changes.

**Good:**
```yaml
# config.yaml
embedding:
  model: "BAAI/bge-base-en-v1.5"
  batch_size: 32

retrieval:
  top_k: 20
  rerank_top_k: 5
```

**Bad:**
```python
# Hard-coded in source
MODEL_NAME = "BAAI/bge-base-en-v1.5"
BATCH_SIZE = 32
```

### Principle 4: Fail Fast, Fail Clearly

Detect errors early and provide helpful messages.

**Good:**
```python
def load_config(path: Path) -> Config:
    if not path.exists():
        raise ConfigError(
            f"Config file not found: {path}\n"
            f"Run 'nexus init' to create one."
        )
```

**Bad:**
```python
def load_config(path: Path) -> Config:
    return yaml.safe_load(path.read_text())  # Cryptic error if missing
```

### Principle 5: Explicit Over Implicit

Make behavior obvious and predictable.

**Good:**
```python
def search(
    self,
    query: str,
    *,  # Force keyword arguments
    limit: int = 10,
    filters: dict[str, Any] | None = None,
    use_reranking: bool = True,
) -> list[SearchResult]:
```

**Bad:**
```python
def search(self, query, n=10, f=None, r=True):  # Unclear parameters
```

---

## 3. Technology Stack

### Core Dependencies (Required)

| Package | Version | Purpose | Why This Choice |
|---------|---------|---------|-----------------|
| `mcp` | >=1.0.0 | MCP protocol | Official SDK |
| `pydantic` | >=2.0.0 | Data validation | Best-in-class validation |
| `pydantic-settings` | >=2.0.0 | Configuration | Type-safe config |
| `sentence-transformers` | >=2.2.0 | Embeddings | Local, high quality |
| `qdrant-client` | >=1.7.0 | Vector storage | Best open-source vector DB |
| `rank-bm25` | >=0.2.2 | Keyword search | Simple, effective BM25 |
| `httpx` | >=0.25.0 | HTTP client | Modern async HTTP |
| `pyyaml` | >=6.0 | Config parsing | YAML support |

### Embedding Models (User Choice)

| Model | Dimensions | Quality | Speed | Recommended For |
|-------|------------|---------|-------|-----------------|
| `BAAI/bge-base-en-v1.5` | 768 | High | Medium | **Default choice** |
| `BAAI/bge-small-en-v1.5` | 384 | Good | Fast | Low-resource systems |
| `nomic-ai/nomic-embed-text-v1.5` | 768 | High | Medium | Alternative |
| `BAAI/bge-large-en-v1.5` | 1024 | Highest | Slow | Maximum quality |

**Default:** `BAAI/bge-base-en-v1.5` — Best balance of quality and speed.

### Reranking Models

| Model | Quality | Speed | Recommended For |
|-------|---------|-------|-----------------|
| `BAAI/bge-reranker-base` | High | Medium | **Default choice** |
| `BAAI/bge-reranker-large` | Highest | Slow | Maximum quality |
| `cross-encoder/ms-marco-MiniLM-L-6-v2` | Good | Fast | Low-resource |

**Default:** `BAAI/bge-reranker-base`

### Optional Dependencies

| Package | Purpose | When Needed |
|---------|---------|-------------|
| `unstructured` | PDF parsing | PDF ingestion |
| `watchdog` | File watching | Auto-index on change |
| `typer` | CLI framework | CLI commands |
| `rich` | Terminal formatting | CLI output |

### Development Dependencies

| Package | Purpose |
|---------|---------|
| `pytest` | Testing framework |
| `pytest-asyncio` | Async test support |
| `pytest-cov` | Coverage reporting |
| `ruff` | Linting and formatting |
| `mypy` | Type checking |
| `pre-commit` | Git hooks |

### Explicitly NOT Using

| Package | Reason |
|---------|--------|
| `langchain` | Too heavy, abstractions hide important details |
| `llama-index` | Same as above |
| `chromadb` | Qdrant is more production-ready |
| `pinecone` | Cloud-only, against local-first principle |
| `fastapi` | No REST API needed, MCP only |
| `flask` | No web server needed |

---

## 4. Project Structure

```
nexus/
├── pyproject.toml           # Project metadata and dependencies
├── README.md                # Project overview and quick start
├── LICENSE                  # MIT License
├── CHANGELOG.md             # Version history
├── CONTRIBUTING.md          # Contribution guidelines
├── Makefile                 # Common development commands
├── docker-compose.yml       # Optional Qdrant setup
│
├── docs/                    # Extended documentation
│   ├── PRD.md              # Product requirements
│   ├── TASKS.md            # Development tasks
│   ├── AGENTS.md           # This file
│   ├── configuration.md    # Config reference
│   └── troubleshooting.md  # Common issues
│
├── src/
│   └── nexus/              # Main package
│       ├── __init__.py     # Package exports
│       ├── __main__.py     # Entry point for `python -m nexus`
│       ├── server.py       # MCP server implementation
│       ├── config.py       # Configuration management
│       ├── exceptions.py   # Custom exceptions
│       │
│       ├── tools/          # MCP tool implementations
│       │   ├── __init__.py
│       │   ├── search.py   # search_knowledge tool
│       │   ├── add.py      # add_note, save_webpage tools
│       │   └── browse.py   # list_sources, get_source tools
│       │
│       ├── rag/            # RAG engine components
│       │   ├── __init__.py
│       │   ├── retriever.py    # Main retrieval orchestration
│       │   ├── embedder.py     # Embedding generation
│       │   ├── reranker.py     # Cross-encoder reranking
│       │   ├── bm25.py         # BM25 keyword search
│       │   └── query.py        # Query processing
│       │
│       ├── ingest/         # Content ingestion
│       │   ├── __init__.py
│       │   ├── base.py         # Base loader interface
│       │   ├── markdown.py     # Markdown loader
│       │   ├── pdf.py          # PDF loader
│       │   ├── readwise.py     # Readwise API sync
│       │   ├── chunker.py      # Semantic chunking
│       │   └── watcher.py      # File system watcher
│       │
│       ├── storage/        # Data persistence
│       │   ├── __init__.py
│       │   ├── base.py         # Storage interfaces
│       │   ├── vectors.py      # Qdrant wrapper
│       │   └── metadata.py     # SQLite wrapper
│       │
│       ├── models/         # Data models
│       │   ├── __init__.py
│       │   ├── document.py     # Document, Chunk models
│       │   ├── source.py       # Source models
│       │   └── search.py       # Search result models
│       │
│       └── cli/            # Command-line interface
│           ├── __init__.py
│           ├── main.py         # CLI entry point
│           ├── init.py         # nexus init command
│           ├── index.py        # nexus index command
│           └── serve.py        # nexus serve command
│
└── tests/                  # Test suite
    ├── conftest.py         # Shared fixtures
    ├── unit/               # Unit tests (mirror src structure)
    │   ├── rag/
    │   ├── ingest/
    │   └── storage/
    ├── integration/        # Integration tests
    └── fixtures/           # Test data
        ├── markdown/
        └── pdfs/
```

### Import Rules

```python
# Public API - what users import
from nexus import NexusServer, Config

# Internal imports - use relative within package
from .rag import Retriever
from ..models import Document

# Never import from tests in source code
# Never import from cli in core modules
```

---

## 5. Coding Standards

### Python Version

**Minimum:** Python 3.10  
**Target:** Python 3.11+

Use modern Python features:
- Type hints everywhere
- `match` statements where appropriate
- `|` for union types (`str | None` not `Optional[str]`)
- Walrus operator where it improves readability

### Type Hints

**Required for:**
- All function parameters
- All function return types
- All class attributes
- All module-level variables

```python
# Good
def search(
    self,
    query: str,
    limit: int = 10,
    filters: dict[str, Any] | None = None,
) -> list[SearchResult]:
    ...

# Bad
def search(self, query, limit=10, filters=None):
    ...
```

### Async/Await

MCP requires async. Follow these patterns:

```python
# MCP tools must be async
@server.tool()
async def search_knowledge(query: str) -> list[SearchResult]:
    results = await retriever.search(query)
    return results

# Internal methods can be sync if no I/O
def process_query(self, query: str) -> ProcessedQuery:
    # Pure computation, no async needed
    return ProcessedQuery(...)

# Use asyncio for concurrent operations
async def index_files(self, paths: list[Path]) -> None:
    tasks = [self._index_file(p) for p in paths]
    await asyncio.gather(*tasks)
```

### Docstrings

Use Google-style docstrings:

```python
def search(
    self,
    query: str,
    limit: int = 10,
    filters: dict[str, Any] | None = None,
) -> list[SearchResult]:
    """Search the knowledge base for relevant content.
    
    Performs hybrid search combining vector similarity and BM25 keyword
    matching, then reranks results using a cross-encoder model.
    
    Args:
        query: The search query string.
        limit: Maximum number of results to return.
        filters: Optional metadata filters. Supported keys:
            - source_type: Filter by source type (note, highlight, article)
            - since: Filter by date (ISO format string)
    
    Returns:
        List of SearchResult objects, ordered by relevance score.
        
    Raises:
        SearchError: If the search operation fails.
        
    Example:
        >>> results = retriever.search("machine learning", limit=5)
        >>> for r in results:
        ...     print(f"{r.score:.2f}: {r.source}")
    """
```

### String Formatting

Use f-strings for formatting:

```python
# Good
message = f"Indexed {count} documents in {elapsed:.2f}s"

# Bad
message = "Indexed {} documents in {:.2f}s".format(count, elapsed)
message = "Indexed %d documents in %.2fs" % (count, elapsed)
```

### Logging

Use structured logging with loguru:

```python
from loguru import logger

# Good - structured with context
logger.info("Indexed documents", count=len(docs), source=source_path)

# Good - appropriate levels
logger.debug("Processing chunk", chunk_id=chunk.id)
logger.warning("Slow query", query=query, elapsed=elapsed)
logger.error("Index failed", error=str(e), path=path)

# Bad - unstructured
logger.info(f"Indexed {len(docs)} documents from {source_path}")
print(f"Error: {e}")  # Never use print for logging
```

---

## 6. Naming Conventions

### Files and Modules

```
lowercase_with_underscores.py

# Good
search_knowledge.py
vector_store.py
markdown_loader.py

# Bad
SearchKnowledge.py
vectorStore.py
markdown-loader.py
```

### Classes

```python
# PascalCase for classes
class VectorStore:
class MarkdownLoader:
class SearchResult:

# Suffix with base type when extending
class QdrantVectorStore(VectorStore):
class ObsidianMarkdownLoader(MarkdownLoader):
```

### Functions and Methods

```python
# snake_case for functions
def search_knowledge():
def load_config():
def process_query():

# Prefix with underscore for private
def _calculate_score():
def _validate_input():
```

### Variables

```python
# snake_case for variables
document_count = 10
search_results = []
config_path = Path("~/.nexus/config.yaml")

# UPPER_CASE for constants
DEFAULT_CHUNK_SIZE = 512
MAX_RESULTS = 100
SUPPORTED_EXTENSIONS = {".md", ".pdf", ".txt"}
```

### Type Aliases

```python
# PascalCase for type aliases
DocumentId = str
Score = float
Embedding = list[float]
Metadata = dict[str, Any]
```

---

## 7. Error Handling

### Custom Exceptions

Define a hierarchy of custom exceptions:

```python
# nexus/exceptions.py

class NexusError(Exception):
    """Base exception for all Nexus errors."""
    pass

class ConfigError(NexusError):
    """Configuration-related errors."""
    pass

class StorageError(NexusError):
    """Storage operation errors."""
    pass

class IngestionError(NexusError):
    """Content ingestion errors."""
    pass

class SearchError(NexusError):
    """Search operation errors."""
    pass

class SourceNotFoundError(NexusError):
    """Requested source does not exist."""
    pass
```

### Error Messages

Make error messages actionable:

```python
# Good - explains what happened and what to do
raise ConfigError(
    f"Knowledge source path does not exist: {path}\n"
    f"Please check your config file at {config_path}\n"
    f"Or run 'nexus init' to reconfigure."
)

# Bad - unhelpful
raise ConfigError("Invalid path")
```

### Try/Except Patterns

```python
# Catch specific exceptions
try:
    result = await self.vector_store.search(query_vector)
except qdrant_client.QdrantException as e:
    logger.error("Vector search failed", error=str(e))
    raise SearchError(f"Vector search failed: {e}") from e

# Never catch bare Exception unless re-raising
try:
    process()
except Exception:
    logger.exception("Unexpected error")
    raise  # Re-raise after logging

# Use contextlib for cleanup
from contextlib import asynccontextmanager

@asynccontextmanager
async def managed_resource():
    resource = await acquire()
    try:
        yield resource
    finally:
        await resource.close()
```

---

## 8. Testing Standards

### Test File Organization

```
tests/
├── unit/                    # Fast, isolated tests
│   ├── rag/
│   │   ├── test_retriever.py
│   │   ├── test_embedder.py
│   │   └── test_chunker.py
│   └── ingest/
│       └── test_markdown.py
├── integration/             # Tests with real dependencies
│   ├── test_full_pipeline.py
│   └── test_mcp_server.py
└── fixtures/                # Test data
    └── markdown/
        ├── simple.md
        └── complex_with_code.md
```

### Test Naming

```python
# test_<module>.py files
# test_<behavior>_<condition> functions

def test_search_returns_relevant_results():
    ...

def test_search_with_filters_applies_correctly():
    ...

def test_search_empty_query_raises_error():
    ...

def test_chunker_preserves_code_blocks():
    ...
```

### Fixtures

Use pytest fixtures for setup:

```python
# conftest.py
import pytest
from nexus.config import Config
from nexus.rag import Retriever

@pytest.fixture
def config() -> Config:
    """Test configuration with in-memory storage."""
    return Config(
        storage=StorageConfig(
            vector_db="memory",
            metadata_db=":memory:",
        )
    )

@pytest.fixture
async def retriever(config: Config) -> Retriever:
    """Configured retriever for testing."""
    r = Retriever(config)
    await r.initialize()
    yield r
    await r.close()

@pytest.fixture
def sample_documents() -> list[Document]:
    """Sample documents for testing."""
    return [
        Document(id="1", content="Machine learning basics", source="test.md"),
        Document(id="2", content="Deep learning neural networks", source="test.md"),
    ]
```

### Test Patterns

```python
# Arrange-Act-Assert pattern
async def test_search_returns_relevant_results(retriever, sample_documents):
    # Arrange
    await retriever.index(sample_documents)
    
    # Act
    results = await retriever.search("machine learning")
    
    # Assert
    assert len(results) > 0
    assert results[0].content == "Machine learning basics"
    assert results[0].score > 0.5

# Parameterized tests for multiple cases
@pytest.mark.parametrize("query,expected_count", [
    ("machine learning", 2),
    ("nonexistent topic", 0),
    ("neural", 1),
])
async def test_search_result_counts(retriever, sample_documents, query, expected_count):
    await retriever.index(sample_documents)
    results = await retriever.search(query)
    assert len(results) == expected_count

# Testing exceptions
async def test_search_empty_query_raises(retriever):
    with pytest.raises(SearchError, match="Query cannot be empty"):
        await retriever.search("")
```

### Coverage Requirements

- **Minimum:** 80% overall coverage
- **Critical paths:** 95% coverage (RAG, MCP tools)
- **Run:** `pytest --cov=nexus --cov-report=html`

### Evaluation Requirements

**See:** [EVALUATION.md](./EVALUATION.md) for complete evaluation framework.

Every change to retrieval logic must:

1. **Run evaluation suite** before merging
2. **Meet thresholds:**
   - Recall@10 ≥ 85%
   - Precision@5 ≥ 80%
   - MRR ≥ 0.70
   - Latency p95 ≤ 500ms
3. **No regressions** > 2% on any metric
4. **Document trade-offs** if accepting minor regression for other gains

**Evaluation is not optional.** A PR that improves code but degrades retrieval quality will be rejected.

---

## 9. Documentation Standards

### Code Comments

```python
# Use comments for WHY, not WHAT

# Bad - describes what code does (obvious)
# Increment counter by 1
counter += 1

# Good - explains why
# Rate limit to avoid overwhelming the embedding API
await asyncio.sleep(0.1)

# Good - explains non-obvious behavior
# BM25 returns raw scores (not normalized), so we normalize here
# to make them comparable with vector similarity scores
normalized_score = score / max_score if max_score > 0 else 0
```

### README Structure

```markdown
# Nexus

One-line description.

## Features

- Feature 1
- Feature 2

## Quick Start

Minimal steps to get running.

## Installation

Detailed installation options.

## Configuration

How to configure.

## Usage

Common usage patterns.

## Contributing

Link to CONTRIBUTING.md

## License

MIT
```

### Changelog Format

```markdown
# Changelog

## [1.1.0] - 2025-02-15

### Added
- PDF ingestion support
- Readwise integration

### Changed
- Improved chunking algorithm

### Fixed
- Memory leak in file watcher

## [1.0.0] - 2025-01-30

### Added
- Initial release
```

---

## 10. Git Workflow

### Branch Naming

```
main                    # Stable, released code
develop                 # Integration branch (optional)
feature/add-pdf-support # New features
fix/memory-leak         # Bug fixes
docs/update-readme      # Documentation
refactor/storage-layer  # Code improvements
```

### Commit Messages

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code change that doesn't fix bug or add feature
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(rag): add cross-encoder reranking

Implement reranking using BGE-reranker-base model.
Improves top-5 precision by ~20% based on evaluation.

Closes #42

---

fix(ingest): handle UTF-8 errors in markdown files

Some markdown files have mixed encodings. Now gracefully
handles errors with replacement characters instead of crashing.

---

docs: add troubleshooting guide for common issues
```

### Pull Request Template

```markdown
## Description

Brief description of changes.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing

How was this tested?

## Checklist

- [ ] Tests pass
- [ ] Documentation updated
- [ ] Changelog updated
```

---

## 11. Decision Framework

When making technical decisions, consider:

### Decision Criteria (In Order)

1. **Does it maintain privacy?**
   - No external data transmission
   - No telemetry
   
2. **Is it simple?**
   - Prefer standard library over dependencies
   - Prefer explicit over magic
   
3. **Is it reliable?**
   - Has good error handling
   - Has tests
   
4. **Is it performant?**
   - Meets latency requirements
   - Doesn't waste resources

### When to Add a Dependency

**Add if:**
- Solves a complex problem correctly (embeddings, vector search)
- Well-maintained and widely used
- No simpler alternative exists

**Avoid if:**
- Could be done with standard library
- Brings many transitive dependencies
- Poorly maintained or abandoned
- Only used in one place

### When to Optimize

**Optimize when:**
- Measurement shows it's a bottleneck
- It affects user experience
- The fix is straightforward

**Don't optimize when:**
- "It might be slow"
- It makes code harder to understand
- Premature (profile first!)

---

## 12. Anti-Patterns to Avoid

### Code Anti-Patterns

```python
# ❌ God objects
class NexusEverything:
    def search(self): ...
    def index(self): ...
    def parse_markdown(self): ...
    def embed(self): ...
    def start_server(self): ...

# ✅ Single responsibility
class Retriever: ...
class Indexer: ...
class MarkdownParser: ...
class Embedder: ...
class MCPServer: ...
```

```python
# ❌ Stringly typed
def process(type: str, data: dict):
    if type == "markdown":
        ...

# ✅ Properly typed
def process(document: MarkdownDocument):
    ...
```

```python
# ❌ Silent failures
def load_file(path):
    try:
        return path.read_text()
    except:
        return ""

# ✅ Explicit errors
def load_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text()
```

### Architecture Anti-Patterns

```
❌ Circular dependencies
module_a imports module_b
module_b imports module_a

✅ Clear dependency direction
ingest → models (not reverse)
rag → storage (not reverse)
tools → rag (not reverse)
```

```
❌ Hardcoded configuration
MODEL = "BAAI/bge-base-en-v1.5"  # In source code

✅ External configuration
model = config.embedding.model  # From config file
```

### Testing Anti-Patterns

```python
# ❌ Testing implementation details
def test_uses_bm25_internally():
    # Fragile - breaks if implementation changes
    assert retriever._bm25_index is not None

# ✅ Testing behavior
def test_finds_keyword_matches():
    # Tests what matters - the results
    results = retriever.search("exact keyword")
    assert any("exact keyword" in r.content for r in results)
```

---

## 13. Performance Guidelines

### Embedding Performance

```python
# ❌ Embed one at a time
for doc in documents:
    embedding = embedder.embed(doc.content)  # Slow!

# ✅ Batch embedding
embeddings = embedder.embed_batch(
    [doc.content for doc in documents],
    batch_size=32
)
```

### Search Performance

```python
# Target latencies
VECTOR_SEARCH_TARGET = 50   # ms
BM25_SEARCH_TARGET = 20     # ms
RERANK_TARGET = 200         # ms
TOTAL_SEARCH_TARGET = 500   # ms

# Monitor and log slow queries
start = time.perf_counter()
results = await search(query)
elapsed = time.perf_counter() - start

if elapsed > 0.5:
    logger.warning("Slow search", query=query, elapsed=elapsed)
```

### Memory Guidelines

```python
# ❌ Load everything into memory
all_documents = list(storage.get_all_documents())  # OOM risk

# ✅ Stream/iterate
async for document in storage.iter_documents():
    process(document)

# ✅ Use generators
def iter_chunks(documents):
    for doc in documents:
        for chunk in chunker.chunk(doc):
            yield chunk
```

---

## 14. Security Guidelines

### Input Validation

```python
# Always validate user input
def search(query: str, limit: int = 10) -> list[SearchResult]:
    if not query or not query.strip():
        raise SearchError("Query cannot be empty")
    
    if limit < 1 or limit > 100:
        raise SearchError("Limit must be between 1 and 100")
    
    query = query.strip()[:1000]  # Limit length
```

### Path Handling

```python
# ❌ Trust user paths
def read_file(path: str):
    return Path(path).read_text()  # Path traversal risk

# ✅ Validate and constrain paths
def read_file(path: Path, base_dir: Path) -> str:
    resolved = (base_dir / path).resolve()
    if not resolved.is_relative_to(base_dir):
        raise SecurityError("Path traversal attempt detected")
    return resolved.read_text()
```

### Secrets Handling

```python
# ❌ Log secrets
logger.info(f"Using API key: {api_key}")

# ✅ Never log secrets
logger.info("Connecting to Readwise API")

# ❌ Hardcode secrets
READWISE_TOKEN = "abc123"

# ✅ Environment variables or secure config
readwise_token = os.environ.get("READWISE_TOKEN")
```

---

## Quick Reference Card

### Before Writing Code

- [ ] Is this the right layer for this code?
- [ ] Does this need a test?
- [ ] Is the interface clean and typed?

### Before Committing

- [ ] `ruff check .` passes
- [ ] `mypy .` passes
- [ ] `pytest` passes
- [ ] Docstrings are complete
- [ ] No secrets in code

### Before PR

- [ ] Tests cover new code
- [ ] Documentation updated
- [ ] Changelog entry added
- [ ] Self-reviewed for clarity

---

## Appendix: Tool Configurations

### pyproject.toml (partial)

```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "C4"]

[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_ignores = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-v --tb=short"
```

### pre-commit config

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic>=2.0]
```

---

*This document should be updated as the project evolves. When in doubt, prioritize simplicity, privacy, and user experience.*
