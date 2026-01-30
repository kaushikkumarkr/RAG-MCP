# Nexus: Development Task Plan
## TASKS.md

**Version:** 1.0  
**Last Updated:** January 2025  
**Estimated Total Duration:** 3-4 weeks

---

## Overview

This document breaks down the Nexus project into phases, milestones, and individual tasks. Each task is designed to be completable in a single focused session (2-4 hours).

### Task Priority Legend

| Priority | Meaning |
|----------|---------|
| 🔴 P0 | Critical — Blocks other work |
| 🟠 P1 | Important — Core functionality |
| 🟡 P2 | Desired — Improves quality |
| 🟢 P3 | Nice-to-have — Future consideration |

### Task Status Legend

| Status | Meaning |
|--------|---------|
| ⬜ | Not started |
| 🔄 | In progress |
| ✅ | Completed |
| ⏸️ | Blocked |
| ❌ | Cancelled |

---

## Phase 0: Project Setup
**Duration:** 1-2 days  
**Goal:** Repository structure, dependencies, and development environment ready

### Milestone 0.1: Repository Initialization

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 0.1.1 | Create GitHub repository with MIT license | 🔴 P0 | ⬜ | None | Include .gitignore for Python |
| 0.1.2 | Set up pyproject.toml with project metadata | 🔴 P0 | ⬜ | 0.1.1 | Use modern Python packaging |
| 0.1.3 | Create directory structure per architecture | 🔴 P0 | ⬜ | 0.1.1 | See AGENTS.md for structure |
| 0.1.4 | Set up development dependencies (pytest, ruff, mypy) | 🟠 P1 | ⬜ | 0.1.2 | Configure in pyproject.toml |
| 0.1.5 | Create initial README.md with project vision | 🟠 P1 | ⬜ | 0.1.1 | Link to PRD for details |
| 0.1.6 | Set up pre-commit hooks for linting | 🟡 P2 | ⬜ | 0.1.4 | ruff + mypy |

### Milestone 0.2: Development Environment

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 0.2.1 | Create docker-compose.yml for Qdrant | 🟠 P1 | ⬜ | 0.1.1 | Optional but recommended |
| 0.2.2 | Create .env.example with all config options | 🟠 P1 | ⬜ | 0.1.2 | Document each variable |
| 0.2.3 | Set up pytest configuration | 🟠 P1 | ⬜ | 0.1.4 | pytest.ini or pyproject.toml |
| 0.2.4 | Create Makefile for common commands | 🟡 P2 | ⬜ | 0.1.2 | install, test, lint, run |

**Phase 0 Exit Criteria:**
- [ ] `pip install -e .` works
- [ ] `pytest` runs (even with no tests)
- [ ] `ruff check .` passes
- [ ] Directory structure matches architecture

---

## Phase 1: Core RAG Foundation
**Duration:** 5-7 days  
**Goal:** Basic search working on markdown files

### Milestone 1.1: Configuration System

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 1.1.1 | Define Pydantic settings models | 🔴 P0 | ⬜ | Phase 0 | EmbeddingConfig, StorageConfig, etc. |
| 1.1.2 | Implement config file loading (YAML) | 🔴 P0 | ⬜ | 1.1.1 | ~/.nexus/config.yaml |
| 1.1.3 | Implement environment variable overrides | 🟠 P1 | ⬜ | 1.1.1 | NEXUS_* prefix |
| 1.1.4 | Add config validation and error messages | 🟠 P1 | ⬜ | 1.1.2 | Clear errors for missing paths |
| 1.1.5 | Write tests for config loading | 🟠 P1 | ⬜ | 1.1.2 | Test defaults, overrides, errors |

### Milestone 1.2: Storage Layer

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 1.2.1 | Define data models (Document, Chunk, Source) | 🔴 P0 | ⬜ | 1.1.1 | Pydantic models |
| 1.2.2 | Implement SQLite metadata store | 🔴 P0 | ⬜ | 1.2.1 | Schema for sources, chunks |
| 1.2.3 | Implement Qdrant vector store wrapper | 🔴 P0 | ⬜ | 1.2.1 | Support embedded + server modes |
| 1.2.4 | Add collection initialization logic | 🟠 P1 | ⬜ | 1.2.3 | Create if not exists |
| 1.2.5 | Implement storage interface abstraction | 🟠 P1 | ⬜ | 1.2.2, 1.2.3 | For testing and future backends |
| 1.2.6 | Write tests for storage operations | 🟠 P1 | ⬜ | 1.2.5 | CRUD operations, edge cases |

### Milestone 1.3: Embedding Pipeline

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 1.3.1 | Implement embedding model loader | 🔴 P0 | ⬜ | 1.1.1 | sentence-transformers |
| 1.3.2 | Add model download/caching logic | 🟠 P1 | ⬜ | 1.3.1 | First-run experience |
| 1.3.3 | Implement batch embedding function | 🔴 P0 | ⬜ | 1.3.1 | Efficient batching |
| 1.3.4 | Add embedding normalization | 🟠 P1 | ⬜ | 1.3.3 | For cosine similarity |
| 1.3.5 | Implement embedding cache (optional) | 🟡 P2 | ⬜ | 1.3.3 | Avoid re-embedding unchanged |
| 1.3.6 | Write tests for embedding pipeline | 🟠 P1 | ⬜ | 1.3.3 | Verify dimensions, consistency |

### Milestone 1.4: Markdown Ingestion

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 1.4.1 | Implement markdown file reader | 🔴 P0 | ⬜ | 1.2.1 | Handle UTF-8, errors |
| 1.4.2 | Implement frontmatter parser | 🟠 P1 | ⬜ | 1.4.1 | YAML frontmatter extraction |
| 1.4.3 | Implement semantic text chunker | 🔴 P0 | ⬜ | 1.4.1 | Paragraph-aware, code-block aware |
| 1.4.4 | Add chunk overlap logic | 🟠 P1 | ⬜ | 1.4.3 | Configurable overlap |
| 1.4.5 | Preserve source attribution in chunks | 🔴 P0 | ⬜ | 1.4.3 | File path, line numbers |
| 1.4.6 | Handle special markdown (tables, code) | 🟠 P1 | ⬜ | 1.4.3 | Keep code blocks intact |
| 1.4.7 | Implement directory walker | 🔴 P0 | ⬜ | 1.4.1 | Recursive, respect .gitignore |
| 1.4.8 | Write tests for markdown ingestion | 🟠 P1 | ⬜ | 1.4.7 | Various markdown formats |

### Milestone 1.5: Basic Vector Search

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 1.5.1 | Implement query embedding | 🔴 P0 | ⬜ | 1.3.3 | Single query to vector |
| 1.5.2 | Implement basic vector search | 🔴 P0 | ⬜ | 1.2.3, 1.5.1 | Top-k retrieval |
| 1.5.3 | Add metadata filtering to search | 🟠 P1 | ⬜ | 1.5.2 | Filter by source, date |
| 1.5.4 | Format search results with sources | 🔴 P0 | ⬜ | 1.5.2 | Include attribution |
| 1.5.5 | Write tests for vector search | 🟠 P1 | ⬜ | 1.5.4 | Relevance, edge cases |

**Phase 1 Exit Criteria:**
- [ ] Can index a folder of markdown files
- [ ] Can search and get relevant results
- [ ] Results include source attribution
- [ ] Tests pass with >80% coverage for new code

---

## Phase 2: Production RAG Quality
**Duration:** 4-5 days  
**Goal:** Hybrid search with reranking, production-quality retrieval

### Milestone 2.1: BM25 Keyword Search

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 2.1.1 | Implement BM25 index builder | 🔴 P0 | ⬜ | 1.4.7 | rank_bm25 library |
| 2.1.2 | Implement BM25 search function | 🔴 P0 | ⬜ | 2.1.1 | Query to ranked results |
| 2.1.3 | Add BM25 index persistence | 🟠 P1 | ⬜ | 2.1.1 | Save/load from disk |
| 2.1.4 | Implement incremental BM25 updates | 🟠 P1 | ⬜ | 2.1.3 | Add new docs without rebuild |
| 2.1.5 | Write tests for BM25 search | 🟠 P1 | ⬜ | 2.1.2 | Keyword matching accuracy |

### Milestone 2.2: Hybrid Search

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 2.2.1 | Implement Reciprocal Rank Fusion | 🔴 P0 | ⬜ | 1.5.2, 2.1.2 | Score combination |
| 2.2.2 | Implement hybrid retriever class | 🔴 P0 | ⬜ | 2.2.1 | Orchestrates both searches |
| 2.2.3 | Add configurable alpha weighting | 🟠 P1 | ⬜ | 2.2.2 | Balance vector vs keyword |
| 2.2.4 | Implement result deduplication | 🟠 P1 | ⬜ | 2.2.2 | Handle overlaps |
| 2.2.5 | Write tests for hybrid search | 🟠 P1 | ⬜ | 2.2.2 | Both search types contribute |

### Milestone 2.3: Cross-Encoder Reranking

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 2.3.1 | Implement reranker model loader | 🔴 P0 | ⬜ | 1.1.1 | BGE-reranker or similar |
| 2.3.2 | Implement rerank function | 🔴 P0 | ⬜ | 2.3.1 | Score query-doc pairs |
| 2.3.3 | Integrate reranker into retrieval pipeline | 🔴 P0 | ⬜ | 2.2.2, 2.3.2 | After hybrid, before return |
| 2.3.4 | Add configurable top-k for reranking | 🟠 P1 | ⬜ | 2.3.3 | Retrieve 20, rerank to 5 |
| 2.3.5 | Write tests for reranking | 🟠 P1 | ⬜ | 2.3.3 | Quality improvement measurable |

### Milestone 2.4: Query Processing

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 2.4.1 | Implement query preprocessor | 🟠 P1 | ⬜ | 2.2.2 | Clean, normalize |
| 2.4.2 | Add filter extraction from query | 🟠 P1 | ⬜ | 2.4.1 | "in my notes" → source filter |
| 2.4.3 | Implement basic query expansion | 🟡 P2 | ⬜ | 2.4.1 | Add related terms |
| 2.4.4 | Write tests for query processing | 🟠 P1 | ⬜ | 2.4.2 | Filter extraction accuracy |

### Milestone 2.5: Evaluation Framework

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 2.5.1 | Define evaluation set schema (YAML format) | 🔴 P0 | ⬜ | 2.2.2 | Query + relevance labels structure |
| 2.5.2 | Build initial evaluation set (50 queries) | 🔴 P0 | ⬜ | 2.5.1 | Mix of synthetic + manual |
| 2.5.3 | Implement Recall@K metric calculation | 🔴 P0 | ⬜ | 2.5.1 | Core retrieval metric |
| 2.5.4 | Implement Precision@K metric calculation | 🔴 P0 | ⬜ | 2.5.1 | Core retrieval metric |
| 2.5.5 | Implement MRR calculation | 🟠 P1 | ⬜ | 2.5.1 | Ranking quality metric |
| 2.5.6 | Implement NDCG@K calculation | 🟠 P1 | ⬜ | 2.5.1 | Comprehensive ranking metric |
| 2.5.7 | Create evaluation runner (runs all queries) | 🔴 P0 | ⬜ | 2.5.3, 2.5.4 | Aggregates all metrics |
| 2.5.8 | Generate evaluation report (markdown) | 🟠 P1 | ⬜ | 2.5.7 | Human-readable output |
| 2.5.9 | Add threshold checking (pass/fail) | 🔴 P0 | ⬜ | 2.5.7 | Fail if below targets |
| 2.5.10 | Expand evaluation set to 100 queries | 🟠 P1 | ⬜ | 2.5.2 | Required before v1.0 |
| 2.5.11 | Add per-category metric breakdown | 🟠 P1 | ⬜ | 2.5.7 | Identify weak spots |
| 2.5.12 | Add latency tracking (p50, p95) | 🟠 P1 | ⬜ | 2.5.7 | Performance metrics |

**Phase 2 Exit Criteria:**
- [ ] Hybrid search returns better results than vector-only
- [ ] Reranking measurably improves top-5 precision
- [ ] Search latency <500ms for 10K documents
- [ ] Tests validate retrieval quality
- [ ] Evaluation framework running with 50+ queries
- [ ] Baseline metrics established: Recall@10, Precision@5, MRR
- [ ] All metrics meet MVP thresholds (Recall≥80%, Precision≥75%, MRR≥0.60)

---

## Phase 3: MCP Server Implementation
**Duration:** 3-4 days  
**Goal:** Fully functional MCP server with all tools

### Milestone 3.1: MCP Server Foundation

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 3.1.1 | Set up MCP server skeleton | 🔴 P0 | ⬜ | Phase 2 | Using official SDK |
| 3.1.2 | Implement server lifecycle (start/stop) | 🔴 P0 | ⬜ | 3.1.1 | Clean shutdown |
| 3.1.3 | Add logging for MCP requests | 🟠 P1 | ⬜ | 3.1.1 | Debug tool calls |
| 3.1.4 | Implement error handling for tools | 🔴 P0 | ⬜ | 3.1.1 | Graceful error responses |
| 3.1.5 | Write tests for MCP server | 🟠 P1 | ⬜ | 3.1.4 | Mock client tests |

### Milestone 3.2: Core MCP Tools

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 3.2.1 | Implement `search_knowledge` tool | 🔴 P0 | ⬜ | 3.1.1, Phase 2 | Primary search tool |
| 3.2.2 | Define tool schema with parameters | 🔴 P0 | ⬜ | 3.2.1 | query, filters, limit |
| 3.2.3 | Format results for MCP response | 🔴 P0 | ⬜ | 3.2.1 | Clear, usable format |
| 3.2.4 | Implement `list_sources` tool | 🟠 P1 | ⬜ | 3.1.1 | Browse indexed content |
| 3.2.5 | Implement `get_source` tool | 🟠 P1 | ⬜ | 3.1.1 | Full source details |
| 3.2.6 | Write tests for core tools | 🟠 P1 | ⬜ | 3.2.3 | Input/output validation |

### Milestone 3.3: Write Tools

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 3.3.1 | Implement `add_note` tool | 🟠 P1 | ⬜ | 3.1.1, 1.4.7 | Create and index note |
| 3.3.2 | Define note storage location | 🟠 P1 | ⬜ | 3.3.1 | Configurable folder |
| 3.3.3 | Implement `save_webpage` tool | 🟡 P2 | ⬜ | 3.1.1 | URL → content → index |
| 3.3.4 | Add web content extraction | 🟡 P2 | ⬜ | 3.3.3 | Clean HTML to text |
| 3.3.5 | Write tests for write tools | 🟠 P1 | ⬜ | 3.3.1 | Verify persistence |

### Milestone 3.4: Advanced Tools

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 3.4.1 | Implement `find_related` tool | 🟡 P2 | ⬜ | 3.2.1 | Cross-reference discovery |
| 3.4.2 | Add similarity-based connections | 🟡 P2 | ⬜ | 3.4.1 | "More like this" |
| 3.4.3 | Write tests for advanced tools | 🟡 P2 | ⬜ | 3.4.1 | Connection quality |

**Phase 3 Exit Criteria:**
- [ ] MCP server starts and responds to tool calls
- [ ] `search_knowledge` returns formatted results
- [ ] Claude Desktop can successfully call tools
- [ ] Error handling is robust

---

## Phase 4: Additional Ingestion Sources
**Duration:** 3-4 days  
**Goal:** PDF support and Readwise integration

### Milestone 4.1: PDF Ingestion

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 4.1.1 | Add unstructured library dependency | 🟠 P1 | ⬜ | Phase 1 | PDF parsing |
| 4.1.2 | Implement PDF text extractor | 🟠 P1 | ⬜ | 4.1.1 | Handle multi-page |
| 4.1.3 | Add PDF metadata extraction | 🟠 P1 | ⬜ | 4.1.2 | Title, author, date |
| 4.1.4 | Integrate PDF with chunking pipeline | 🟠 P1 | ⬜ | 4.1.2, 1.4.3 | Use semantic chunker |
| 4.1.5 | Handle PDF edge cases | 🟠 P1 | ⬜ | 4.1.2 | Scanned, encrypted, corrupt |
| 4.1.6 | Write tests for PDF ingestion | 🟠 P1 | ⬜ | 4.1.4 | Various PDF types |

### Milestone 4.2: Readwise Integration

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 4.2.1 | Implement Readwise API client | 🟠 P1 | ⬜ | Phase 1 | Auth, pagination |
| 4.2.2 | Fetch highlights and books | 🟠 P1 | ⬜ | 4.2.1 | Full sync |
| 4.2.3 | Map Readwise data to Nexus schema | 🟠 P1 | ⬜ | 4.2.2 | Source, metadata |
| 4.2.4 | Implement incremental sync | 🟠 P1 | ⬜ | 4.2.2 | Only new highlights |
| 4.2.5 | Add sync scheduling option | 🟡 P2 | ⬜ | 4.2.4 | Periodic background sync |
| 4.2.6 | Write tests for Readwise sync | 🟠 P1 | ⬜ | 4.2.4 | Mock API responses |

### Milestone 4.3: File Watching

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 4.3.1 | Implement file system watcher | 🟠 P1 | ⬜ | Phase 1 | watchdog library |
| 4.3.2 | Handle file create/modify/delete events | 🟠 P1 | ⬜ | 4.3.1 | Appropriate actions |
| 4.3.3 | Add debouncing for rapid changes | 🟠 P1 | ⬜ | 4.3.2 | Avoid over-processing |
| 4.3.4 | Implement background watcher thread | 🟠 P1 | ⬜ | 4.3.1 | Non-blocking |
| 4.3.5 | Add watcher status reporting | 🟡 P2 | ⬜ | 4.3.4 | CLI status command |
| 4.3.6 | Write tests for file watching | 🟠 P1 | ⬜ | 4.3.2 | Event handling |

**Phase 4 Exit Criteria:**
- [ ] PDFs are indexed and searchable
- [ ] Readwise highlights sync and are searchable
- [ ] File changes are auto-detected and indexed
- [ ] All sources maintain proper attribution

---

## Phase 5: CLI and User Experience
**Duration:** 2-3 days  
**Goal:** Complete CLI for setup and management

### Milestone 5.1: CLI Foundation

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 5.1.1 | Set up Typer CLI application | 🟠 P1 | ⬜ | Phase 3 | Main entry point |
| 5.1.2 | Add Rich for formatted output | 🟠 P1 | ⬜ | 5.1.1 | Tables, progress |
| 5.1.3 | Implement `nexus --version` | 🟠 P1 | ⬜ | 5.1.1 | Version info |
| 5.1.4 | Implement `nexus --help` with examples | 🟠 P1 | ⬜ | 5.1.1 | Clear documentation |

### Milestone 5.2: Setup Commands

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 5.2.1 | Implement `nexus init` command | 🔴 P0 | ⬜ | 5.1.1, 1.1.2 | Create config file |
| 5.2.2 | Add interactive source configuration | 🟠 P1 | ⬜ | 5.2.1 | Prompt for paths |
| 5.2.3 | Implement `nexus config show` | 🟠 P1 | ⬜ | 5.2.1 | Display current config |
| 5.2.4 | Implement `nexus config set` | 🟡 P2 | ⬜ | 5.2.1 | Modify config values |

### Milestone 5.3: Index Commands

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 5.3.1 | Implement `nexus index` command | 🔴 P0 | ⬜ | 5.1.1, Phase 1 | Full reindex |
| 5.3.2 | Add progress bar for indexing | 🟠 P1 | ⬜ | 5.3.1 | Rich progress |
| 5.3.3 | Implement `nexus index --source` | 🟠 P1 | ⬜ | 5.3.1 | Index specific source |
| 5.3.4 | Implement `nexus status` command | 🟠 P1 | ⬜ | 5.1.1 | Index stats, health |

### Milestone 5.4: Search Commands

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 5.4.1 | Implement `nexus search` command | 🟠 P1 | ⬜ | 5.1.1, Phase 2 | CLI search |
| 5.4.2 | Format search results nicely | 🟠 P1 | ⬜ | 5.4.1 | Rich formatting |
| 5.4.3 | Add filter flags (--source, --type) | 🟡 P2 | ⬜ | 5.4.1 | CLI filtering |

### Milestone 5.5: Server Commands

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 5.5.1 | Implement `nexus serve` command | 🔴 P0 | ⬜ | 5.1.1, Phase 3 | Start MCP server |
| 5.5.2 | Add daemon mode option | 🟡 P2 | ⬜ | 5.5.1 | Background running |
| 5.5.3 | Implement graceful shutdown | 🟠 P1 | ⬜ | 5.5.1 | SIGTERM handling |

**Phase 5 Exit Criteria:**
- [ ] `nexus init` creates working config
- [ ] `nexus index` processes all sources with progress
- [ ] `nexus serve` starts MCP server
- [ ] `nexus status` shows index health

---

## Phase 6: Documentation and Release
**Duration:** 2-3 days  
**Goal:** Production-ready release

### Milestone 6.1: Documentation

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 6.1.1 | Write comprehensive README.md | 🔴 P0 | ⬜ | All phases | Installation, quick start |
| 6.1.2 | Create CONTRIBUTING.md | 🟠 P1 | ⬜ | 6.1.1 | How to contribute |
| 6.1.3 | Write configuration reference | 🟠 P1 | ⬜ | 6.1.1 | All config options |
| 6.1.4 | Create Claude Desktop setup guide | 🔴 P0 | ⬜ | 6.1.1 | Step-by-step with screenshots |
| 6.1.5 | Write Moltbot integration guide | 🟠 P1 | ⬜ | 6.1.1 | Moltbot-specific setup |
| 6.1.6 | Document all MCP tools | 🟠 P1 | ⬜ | 6.1.1 | Parameters, examples |
| 6.1.7 | Create troubleshooting guide | 🟠 P1 | ⬜ | 6.1.1 | Common issues |

### Milestone 6.2: Testing and Quality

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 6.2.1 | Achieve >80% test coverage | 🟠 P1 | ⬜ | All phases | Run coverage report |
| 6.2.2 | Create integration test suite | 🟠 P1 | ⬜ | All phases | End-to-end tests |
| 6.2.3 | Performance benchmarks | 🟡 P2 | ⬜ | All phases | Latency, memory |
| 6.2.4 | Manual QA on different OS | 🟠 P1 | ⬜ | All phases | Mac, Linux, Windows |
| 6.2.5 | Add evaluation to CI pipeline | 🔴 P0 | ⬜ | 2.5.7 | Run on every PR |
| 6.2.6 | Implement CI threshold checks | 🔴 P0 | ⬜ | 6.2.5 | Fail build if below targets |
| 6.2.7 | Add regression detection to CI | 🟠 P1 | ⬜ | 6.2.5 | Compare to baseline, flag drops >2% |
| 6.2.8 | Create PR comment template for eval results | 🟠 P1 | ⬜ | 6.2.5 | Show metrics in PR |
| 6.2.9 | Expand evaluation set to 100+ queries | 🔴 P0 | ⬜ | 2.5.10 | Required for v1.0 |
| 6.2.10 | Validate eval set meets production thresholds | 🔴 P0 | ⬜ | 6.2.9 | Recall≥85%, Precision≥80%, MRR≥0.70 |

### Milestone 6.3: Release Preparation

| ID | Task | Priority | Status | Dependencies | Notes |
|----|------|----------|--------|--------------|-------|
| 6.3.1 | Create CHANGELOG.md | 🟠 P1 | ⬜ | All phases | Version history |
| 6.3.2 | Set up GitHub Actions for CI | 🟠 P1 | ⬜ | 6.2.1 | Test on push |
| 6.3.3 | Configure PyPI publishing | 🔴 P0 | ⬜ | 6.3.2 | pip install nexus-knowledge |
| 6.3.4 | Create GitHub release | 🔴 P0 | ⬜ | 6.3.3 | v1.0.0 |
| 6.3.5 | Write announcement post | 🟡 P2 | ⬜ | 6.3.4 | Blog/social media |

**Phase 6 Exit Criteria:**
- [ ] README enables self-serve setup
- [ ] Tests pass on CI
- [ ] Package published to PyPI
- [ ] v1.0.0 released on GitHub
- [ ] Evaluation runs in CI on every PR
- [ ] All quality thresholds met: Recall@10≥85%, Precision@5≥80%, MRR≥0.70
- [ ] 100+ queries in evaluation set
- [ ] No regressions in final release vs baseline

---

## Dependency Graph

```
Phase 0 (Setup)
    │
    ▼
Phase 1 (Core RAG) ─────────────────┐
    │                               │
    ▼                               │
Phase 2 (Production RAG)            │
    │                               │
    ▼                               │
Phase 3 (MCP Server) ◄──────────────┘
    │
    ├──────────────────┐
    ▼                  ▼
Phase 4 (Sources)   Phase 5 (CLI)
    │                  │
    └────────┬─────────┘
             ▼
      Phase 6 (Release)
```

---

## Daily Standup Template

Use this for tracking progress:

```markdown
## Date: YYYY-MM-DD

### Completed Yesterday
- [ ] Task ID: Description

### Plan for Today
- [ ] Task ID: Description

### Blockers
- None / Description of blocker

### Notes
- Any observations or decisions made
```

---

## Risk Checkpoints

After each phase, evaluate:

| Question | Yes/No | Action if No |
|----------|--------|--------------|
| Tests passing? | | Fix before proceeding |
| Performance acceptable? | | Profile and optimize |
| Documentation updated? | | Update before forgetting |
| Code reviewed/clean? | | Refactor technical debt |
| On schedule? | | Re-prioritize or cut scope |

---

## Definition of Done

A task is complete when:

1. ✅ Code is written and working
2. ✅ Unit tests are written and passing
3. ✅ Type hints are complete
4. ✅ Docstrings are written
5. ✅ Linting passes (ruff, mypy)
6. ✅ Edge cases are handled
7. ✅ Error messages are helpful

A phase is complete when:

1. ✅ All P0 and P1 tasks are done
2. ✅ Exit criteria are met
3. ✅ Integration tested
4. ✅ No critical bugs
5. ✅ Evaluation metrics meet phase thresholds (if applicable)
6. ✅ No regression from previous phase baseline

---

## Time Estimates Summary

| Phase | Duration | Effort |
|-------|----------|--------|
| Phase 0: Setup | 1-2 days | 8-16 hours |
| Phase 1: Core RAG | 5-7 days | 40-56 hours |
| Phase 2: Production RAG | 4-5 days | 32-40 hours |
| Phase 3: MCP Server | 3-4 days | 24-32 hours |
| Phase 4: Sources | 3-4 days | 24-32 hours |
| Phase 5: CLI | 2-3 days | 16-24 hours |
| Phase 6: Release | 2-3 days | 16-24 hours |
| **Total** | **20-28 days** | **160-224 hours** |

Assuming 4-6 productive hours per day, expect **3-5 weeks** to v1.0.

---

## Quick Reference: What to Build First

If you have limited time, prioritize in this order:

1. **Minimum Viable Product (1 week)**
   - Config system
   - Markdown ingestion
   - Basic vector search
   - MCP server with `search_knowledge`

2. **Usable Product (2 weeks)**
   - Add BM25 hybrid search
   - Add reranking
   - Add CLI commands
   - Basic documentation

3. **Production Product (3-4 weeks)**
   - PDF and Readwise support
   - File watching
   - Comprehensive docs
   - Full test coverage
