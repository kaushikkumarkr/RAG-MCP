# Nexus: Personal Knowledge MCP Server
## Product Requirements Document (PRD)

**Version:** 1.0  
**Last Updated:** January 2025  
**Author:** Kaushik  
**Status:** Draft

---

## Executive Summary

Nexus is an open-source MCP (Model Context Protocol) server that provides production-grade RAG (Retrieval-Augmented Generation) capabilities to any MCP-compatible client. It transforms scattered personal knowledge (notes, highlights, saved articles, documents) into an intelligently searchable knowledge base that AI assistants can query on your behalf.

**The Core Problem:** Claude Desktop, Moltbot, and other MCP clients can read files, but they cannot semantically search across large knowledge bases. Users with hundreds or thousands of notes, highlights, and documents cannot leverage this knowledge effectively.

**The Solution:** Nexus indexes your personal knowledge, embeds it semantically, and exposes intelligent search via MCP tools — enabling any MCP client to answer questions like "What do I know about X?" across your entire knowledge base.

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Vision & Goals](#2-vision--goals)
3. [Target Users](#3-target-users)
4. [User Stories](#4-user-stories)
5. [Core Features](#5-core-features)
6. [Non-Goals](#6-non-goals)
7. [Success Metrics](#7-success-metrics)
8. [Technical Requirements](#8-technical-requirements)
9. [User Experience](#9-user-experience)
10. [Privacy & Security](#10-privacy--security)
11. [Competitive Analysis](#11-competitive-analysis)
12. [Risks & Mitigations](#12-risks--mitigations)
13. [Future Roadmap](#13-future-roadmap)

---

## 1. Problem Statement

### The Knowledge Fragmentation Problem

Modern knowledge workers accumulate vast amounts of information:
- Notes in Obsidian, Notion, or plain markdown
- Book highlights in Kindle or Readwise
- Saved articles in Pocket, Instapaper, or browser bookmarks
- PDFs, research papers, and documents
- Personal journals and reflections

This knowledge is:
- **Scattered** across multiple apps and formats
- **Siloed** with no cross-referencing
- **Forgotten** because it's too hard to search effectively
- **Underutilized** when making decisions or creating content

### The AI Assistant Limitation

Current AI assistants (Claude Desktop, Moltbot, etc.) can:
- ✅ Read individual files via MCP
- ✅ Process content within their context window
- ✅ Access external tools and APIs

But they cannot:
- ❌ Semantically search large document collections
- ❌ Find relevant information across hundreds/thousands of files
- ❌ Handle knowledge bases that exceed context window limits
- ❌ Retrieve information based on meaning, not just keywords

### The Gap

There is no simple, open-source solution that:
1. Works with existing MCP clients (no new apps to learn)
2. Indexes personal knowledge locally (privacy-preserving)
3. Provides production-quality RAG (not toy demos)
4. Requires minimal setup (not enterprise complexity)

**Nexus fills this gap.**

---

## 2. Vision & Goals

### Vision Statement

> "Your AI assistant should know everything you know."

Nexus makes your accumulated knowledge instantly accessible to any AI assistant, transforming passive information storage into active intelligence augmentation.

### Primary Goals

| Goal | Description | Measure |
|------|-------------|---------|
| **G1: Seamless Integration** | Work with any MCP client without modification | Compatible with Claude Desktop, Moltbot, and standard MCP protocol |
| **G2: Production RAG Quality** | Retrieval quality comparable to commercial solutions | >85% relevance in top-5 results |
| **G3: Simple Setup** | Users can start in under 10 minutes | Single pip install + config file edit |
| **G4: Privacy First** | All data stays local, no cloud dependency | Zero external data transmission |
| **G5: Extensible** | Easy to add new knowledge sources | Plugin architecture for loaders |

### Secondary Goals

- Demonstrate production RAG patterns for learning/portfolio
- Build open-source community around personal knowledge tools
- Create foundation for future proactive knowledge features

---

## 3. Target Users

### Primary Persona: Knowledge Worker "Alex"

**Demographics:**
- Age: 25-45
- Occupation: Developer, researcher, writer, analyst, student
- Technical ability: Comfortable with command line and config files

**Behaviors:**
- Takes notes regularly (Obsidian, Notion, markdown)
- Saves articles and highlights from books
- Uses Claude Desktop or similar AI tools daily
- Has 100-10,000+ documents accumulated over years

**Pain Points:**
- "I know I read something about this, but can't find it"
- "My notes are scattered across too many places"
- "Claude can't access my knowledge effectively"
- "Existing tools require too much manual organization"

**Goals:**
- Leverage past learning when making decisions
- Stop re-researching topics they've already studied
- Have AI understand their personal context

### Secondary Persona: Developer "Jordan"

**Demographics:**
- Age: 22-40
- Occupation: Software developer, AI engineer
- Technical ability: High, contributes to open source

**Behaviors:**
- Building AI applications
- Learning RAG systems
- Looking for reference implementations

**Goals:**
- Understand production RAG architecture
- Customize for specific use cases
- Contribute improvements back

---

## 4. User Stories

### Epic 1: Knowledge Ingestion

| ID | User Story | Priority | Acceptance Criteria |
|----|------------|----------|---------------------|
| US-1.1 | As a user, I want to point Nexus at my Obsidian vault so that all my notes are automatically indexed | P0 | Recursively indexes all .md files, handles frontmatter, preserves wikilinks |
| US-1.2 | As a user, I want to add a folder of PDFs so that I can search my research papers | P1 | Extracts text from PDFs, handles multi-page documents, preserves source reference |
| US-1.3 | As a user, I want to sync my Readwise highlights so that my book learnings are searchable | P1 | OAuth or token auth, syncs highlights and notes, includes book metadata |
| US-1.4 | As a user, I want new files to be automatically detected so that I don't have to manually re-index | P0 | File watcher detects changes within 30 seconds, incremental indexing |
| US-1.5 | As a user, I want to save web pages for later search | P2 | Provide URL, content is fetched, cleaned, and indexed |

### Epic 2: Knowledge Retrieval

| ID | User Story | Priority | Acceptance Criteria |
|----|------------|----------|---------------------|
| US-2.1 | As a user, I want to search my knowledge semantically so that I find relevant content even with different wording | P0 | Semantic search returns conceptually related content, not just keyword matches |
| US-2.2 | As a user, I want results to cite their source so that I can verify and read more | P0 | Every result includes source file, location, and direct link if possible |
| US-2.3 | As a user, I want to filter by source type so that I can search only my notes or only my highlights | P1 | Metadata filters for source, date range, tags, document type |
| US-2.4 | As a user, I want to find connections across sources so that I discover related ideas | P2 | Cross-reference detection, related content suggestions |
| US-2.5 | As a user, I want fast results so that the AI conversation feels natural | P0 | Search completes in <500ms for 10,000 documents |

### Epic 3: MCP Integration

| ID | User Story | Priority | Acceptance Criteria |
|----|------------|----------|---------------------|
| US-3.1 | As a user, I want Nexus to work with Claude Desktop so that Claude can search my knowledge | P0 | Standard MCP protocol, documented config |
| US-3.2 | As a user, I want Nexus to work with Moltbot so that I can use my preferred client | P0 | Compatible with any MCP-compliant client |
| US-3.3 | As a user, I want to add notes via the AI conversation so that quick thoughts are captured | P1 | `add_note` tool creates indexed document |
| US-3.4 | As a user, I want to browse my knowledge sources so that I understand what's indexed | P1 | `list_sources` and `get_source` tools |

### Epic 4: Setup & Operations

| ID | User Story | Priority | Acceptance Criteria |
|----|------------|----------|---------------------|
| US-4.1 | As a user, I want simple installation so that I can start quickly | P0 | Single `pip install` command works |
| US-4.2 | As a user, I want clear documentation so that I understand how to configure | P0 | README covers all setup scenarios |
| US-4.3 | As a user, I want to see indexing status so that I know it's working | P1 | CLI command shows indexed count, last update, any errors |
| US-4.4 | As a user, I want minimal resource usage so that it doesn't slow my computer | P1 | <500MB RAM idle, <2GB during indexing |

---

## 5. Core Features

### Feature 1: Multi-Format Knowledge Ingestion

**Description:** Automatically ingest and process documents from multiple sources and formats.

**Supported Sources (v1.0):**
| Source | Format | Method |
|--------|--------|--------|
| Obsidian | Markdown | File system watch |
| Logseq | Markdown | File system watch |
| Plain markdown | .md files | File system watch |
| PDF documents | .pdf | File system watch |
| Readwise | API | Periodic sync |

**Processing Pipeline:**
1. **Detection** — File watcher or API poll detects new/changed content
2. **Parsing** — Source-specific parser extracts text and metadata
3. **Chunking** — Semantic chunker splits into retrievable units
4. **Embedding** — Local embedding model generates vectors
5. **Storage** — Vectors and metadata stored in local databases

**Key Capabilities:**
- Incremental indexing (only process changes)
- Preserve source attribution through entire pipeline
- Handle special content (code blocks, tables, images as captions)
- Extract and index metadata (tags, dates, titles)

---

### Feature 2: Production RAG Engine

**Description:** High-quality retrieval using industry best practices.

**RAG Pipeline:**

```
Query → Query Processing → Hybrid Retrieval → Reranking → Results

Query Processing:
├── Intent detection (what type of search)
├── Query expansion (add related terms)
└── Filter extraction (date, source, type)

Hybrid Retrieval:
├── Vector search (semantic similarity)
├── BM25 search (keyword matching)
└── Metadata filtering (structured constraints)

Reranking:
├── Score fusion (RRF algorithm)
├── Cross-encoder reranking (deep relevance)
└── Diversity sampling (avoid redundancy)
```

**Quality Targets:**
| Metric | Target | Measurement |
|--------|--------|-------------|
| Recall@10 | >90% | Relevant chunk in top 10 results |
| Precision@5 | >80% | Top 5 results are relevant |
| Latency p50 | <200ms | Median search time |
| Latency p95 | <500ms | 95th percentile search time |

---

### Feature 3: MCP Tool Interface

**Description:** Expose knowledge capabilities via standard MCP protocol.

**Tools Exposed:**

| Tool | Purpose | Parameters |
|------|---------|------------|
| `search_knowledge` | Semantic search across all knowledge | `query`, `filters`, `limit` |
| `add_note` | Create new note in knowledge base | `content`, `title`, `tags` |
| `save_webpage` | Save and index a web page | `url`, `highlights` |
| `find_related` | Find connections to a topic | `topic`, `limit` |
| `list_sources` | Browse indexed sources | `type`, `since` |
| `get_source` | Get full source details | `source_id` |

**Response Format:**
```
SearchResult:
  - chunk_id: unique identifier
  - content: the relevant text
  - source: where it came from
  - source_type: (note, highlight, article, pdf)
  - relevance_score: 0-1 confidence
  - metadata: (date, tags, title, author)
```

---

### Feature 4: Local-First Architecture

**Description:** All processing and storage happens locally.

**Privacy Guarantees:**
- No data sent to external servers (except user-chosen LLM API)
- All embeddings generated locally
- Vector database runs locally
- No telemetry or analytics

**Deployment Options:**
| Option | Complexity | Performance |
|--------|------------|-------------|
| Embedded Qdrant | Lowest | Good for <50K docs |
| Docker Qdrant | Low | Best for large collections |
| SQLite only | Lowest | Acceptable for <10K docs |

---

## 6. Non-Goals

The following are explicitly NOT goals for v1.0:

| Non-Goal | Rationale |
|----------|-----------|
| **Build a chat UI** | MCP clients provide this |
| **Handle LLM inference** | MCP clients provide this |
| **Real-time collaboration** | Personal knowledge, single user |
| **Cloud sync** | Privacy-first, local-only |
| **Mobile app** | Desktop MCP clients are target |
| **Note-taking features** | Integrate with existing tools, don't replace |
| **OCR for images** | Complex, add in future version |
| **Audio/video transcription** | Complex, add in future version |

---

## 7. Success Metrics

**See also:** [EVALUATION.md](./EVALUATION.md) for detailed evaluation methodology, metrics definitions, and quality thresholds.

### Adoption Metrics

| Metric | 3-Month Target | 6-Month Target |
|--------|----------------|----------------|
| GitHub stars | 500 | 2,000 |
| PyPI downloads | 1,000 | 5,000 |
| Active issues/PRs | 20 | 50 |
| Community contributors | 5 | 15 |

### Quality Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Retrieval relevance | >85% | Evaluation test suite |
| Search latency p95 | <500ms | Automated benchmarks |
| Indexing speed | >100 docs/min | Automated benchmarks |
| Memory usage (idle) | <500MB | Profiling |

### User Satisfaction Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Setup success rate | >90% | GitHub issues analysis |
| "Works as expected" | >80% | User feedback |
| Continued usage (30 days) | >60% | Self-reported |

---

## 8. Technical Requirements

### System Requirements

**Minimum:**
- OS: macOS 12+, Ubuntu 20.04+, Windows 10+
- Python: 3.10+
- RAM: 8GB (16GB recommended)
- Storage: 2GB + space for vector index
- CPU: Any modern x86_64 or ARM64

**Recommended:**
- RAM: 16GB+
- SSD storage for fast indexing
- Multi-core CPU for parallel embedding

### Dependencies

**Core:**
- Python 3.10+
- MCP SDK (official)
- Sentence-Transformers
- Qdrant Client
- SQLite (built-in)

**Optional:**
- Docker (for Qdrant server)
- Redis (for caching)

### Performance Requirements

| Operation | Requirement |
|-----------|-------------|
| Initial indexing | >100 documents/minute |
| Incremental indexing | <5 seconds for single document |
| Search latency | <500ms p95 |
| Memory (idle) | <500MB |
| Memory (indexing) | <2GB peak |
| Disk (index) | ~1KB per document (vectors + metadata) |

---

## 9. User Experience

### Installation Flow

```
Step 1: Install
$ pip install nexus-knowledge

Step 2: Initialize
$ nexus init
→ Creates ~/.nexus/config.yaml
→ Prompts for knowledge source paths

Step 3: Configure MCP Client
→ Add to claude_desktop_config.json
→ Restart Claude Desktop

Step 4: First Index
$ nexus index
→ Processes all configured sources
→ Shows progress and summary

Step 5: Verify
→ In Claude Desktop: "Search my knowledge for [topic]"
→ Should return relevant results
```

### Daily Usage

**Passive:** Nexus watches for file changes and auto-indexes in background.

**Active via AI:**
```
User: "What do I know about building habits?"

Claude: [Calls nexus.search_knowledge]

Based on your knowledge base, I found several relevant sources:

From "Atomic Habits" highlights:
- [Key insight 1]
- [Key insight 2]

From your notes "Morning Routine":
- [Your personal observation]

From saved article "The Science of Habits":
- [Relevant excerpt]

Would you like me to expand on any of these?
```

### Error Handling

| Scenario | User Experience |
|----------|-----------------|
| Source folder not found | Clear error message with path, suggestion to check config |
| Indexing fails for file | Log warning, continue with other files, report summary |
| Search returns no results | Suggest query modifications, confirm index is populated |
| MCP connection fails | Provide troubleshooting steps in error message |

---

## 10. Privacy & Security

### Data Handling Principles

1. **Local Processing** — All computation happens on user's machine
2. **No Telemetry** — No usage data collected or transmitted
3. **User Ownership** — All data stored in user-accessible locations
4. **Transparent Storage** — SQLite and Qdrant formats are inspectable

### Data Flow

```
User's Files → Nexus (local) → Local Vector DB
                    ↓
              MCP Protocol
                    ↓
              MCP Client → LLM API (user's choice)
```

**What stays local:**
- Original documents
- Embeddings
- Vector index
- Metadata database
- Search queries and results

**What may be sent externally:**
- Search results sent to LLM (user's configured provider)
- This is handled by MCP client, not Nexus

### Security Considerations

| Risk | Mitigation |
|------|------------|
| Sensitive content in knowledge base | User controls what folders to index |
| MCP exposes data to any client | User controls which clients connect |
| Embeddings could theoretically be reversed | Use local embedding model, no external API |

---

## 11. Competitive Analysis

### Direct Alternatives

| Solution | Pros | Cons | Nexus Advantage |
|----------|------|------|-----------------|
| **Mem.ai** | Polished UX, AI-native | Closed source, cloud-only, $$ | Local, free, MCP-integrated |
| **Rewind.ai** | Automatic capture | Mac-only, privacy concerns, $$ | Cross-platform, explicit indexing |
| **Khoj** | Open source, self-hosted | Complex setup, own UI | Simpler, MCP-native |
| **Obsidian + Copilot** | Integrated with Obsidian | Obsidian-only, limited RAG | Source-agnostic, production RAG |

### Indirect Alternatives

| Solution | Limitation |
|----------|------------|
| **Manual search** | Doesn't scale, misses connections |
| **Full-text search (grep)** | No semantic understanding |
| **Claude with file MCP** | No persistence, context limits |
| **Custom RAG scripts** | Not reusable, requires expertise |

### Competitive Positioning

Nexus is the only solution that:
1. ✅ Works with any MCP client (not siloed)
2. ✅ Fully open source and local
3. ✅ Production-quality RAG (not toy)
4. ✅ Simple setup (not enterprise)

---

## 12. Risks & Mitigations

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Embedding model quality insufficient | Low | High | Use proven BGE/E5 models, make swappable |
| Performance issues at scale | Medium | Medium | Benchmark regularly, optimize hot paths |
| MCP protocol changes | Low | High | Depend only on stable MCP features |
| Qdrant complexity for users | Medium | Medium | Support embedded mode, SQLite fallback |

### Adoption Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Setup too complex | Medium | High | Focus on single-command install, clear docs |
| Users don't have enough content | Low | Medium | Work well with small collections too |
| Better solution emerges | Medium | Medium | Stay focused, build community |

### Operational Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Maintainer burnout | Medium | High | Build contributor community early |
| Dependency breaks | Low | Medium | Pin versions, test matrix |

---

## 13. Future Roadmap

### Version 1.0 (MVP)

Focus: Core RAG functionality with essential sources

- Markdown/Obsidian ingestion
- PDF ingestion
- Readwise sync
- Hybrid search (vector + BM25)
- Cross-encoder reranking
- MCP tool interface
- Basic CLI

### Version 1.1

Focus: Expanded sources and improved UX

- Pocket integration
- Kindle highlights (export file)
- Browser bookmarks
- Web page saving
- Better progress reporting
- Search quality metrics

### Version 1.2

Focus: Intelligence layer

- Automatic connection discovery
- Topic clustering
- Knowledge gap detection
- Daily digest generation
- Proactive suggestions

### Version 2.0

Focus: Advanced features

- Graph-based retrieval
- Multi-modal (images with captions)
- Custom embedding fine-tuning
- Plugin system for sources
- Collaborative knowledge (shared bases)

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **MCP** | Model Context Protocol — Standard for AI tool integration |
| **RAG** | Retrieval-Augmented Generation — Finding relevant context before generating |
| **Embedding** | Vector representation of text capturing semantic meaning |
| **Chunking** | Splitting documents into retrievable units |
| **Reranking** | Second-pass scoring for higher precision |
| **BM25** | Traditional keyword-based search algorithm |
| **Cross-encoder** | Model that scores query-document pairs together |

---

## Appendix B: References

- MCP Specification: https://modelcontextprotocol.io
- Sentence-Transformers: https://www.sbert.net
- Qdrant: https://qdrant.tech
- BGE Embeddings: https://huggingface.co/BAAI/bge-base-en-v1.5
- RAG Best Practices: Various Anthropic and OpenAI documentation

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Jan 2025 | Kaushik | Initial draft |
