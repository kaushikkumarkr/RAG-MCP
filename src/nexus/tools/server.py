"""Nexus MCP Server implementation."""

import asyncio
from pathlib import Path
from typing import Any

from loguru import logger
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import INTERNAL_ERROR, TextContent, Tool

from nexus.config import Config, load_config
from nexus.ingest.pipeline import IngestionPipeline
from nexus.ingest.chunker import TextChunker
from nexus.ingest.loader import MarkdownLoader
from nexus.rag.embedder import Embedder
from nexus.rag.hybrid import HybridSearchEngine
from nexus.rag.bm25 import BM25Index
from nexus.storage.metadata import MetadataStore
from nexus.storage.vectors import VectorStore
from nexus.memory.store import MemoryStore, MemoryType


class NexusServer:
    """Nexus MCP server for knowledge retrieval."""

    def __init__(
        self,
        config: Config | None = None,
        config_path: Path | None = None,
    ) -> None:
        """Initialize Nexus server.

        Args:
            config: Configuration object
            config_path: Path to config file (used if config not provided)
        """
        if config is None:
            config = load_config(config_path) if config_path else Config()
        self.config = config

        # Initialize components lazily
        self._embedder: Embedder | None = None
        self._metadata_store: MetadataStore | None = None
        self._vector_store: VectorStore | None = None
        self._search_engine: HybridSearchEngine | None = None
        self._pipeline: IngestionPipeline | None = None
        self._memory_store: MemoryStore | None = None

        # Create MCP server
        self.server = Server("nexus")
        self._setup_handlers()

    @property
    def embedder(self) -> Embedder:
        """Lazy-load embedder."""
        if self._embedder is None:
            self._embedder = Embedder(
                model_name=self.config.embedding.model,
                batch_size=self.config.embedding.batch_size,
                normalize=self.config.embedding.normalize,
            )
        return self._embedder

    @property
    def metadata_store(self) -> MetadataStore:
        """Lazy-load metadata store."""
        if self._metadata_store is None:
            self._metadata_store = MetadataStore(self.config.storage.metadata_db)
        return self._metadata_store

    @property
    def vector_store(self) -> VectorStore:
        """Lazy-load vector store."""
        if self._vector_store is None:
            self._vector_store = VectorStore(
                collection_name=self.config.storage.collection_name,
                path=self.config.storage.qdrant_path,
                embedding_dim=self.embedder.dimension,
            )
        return self._vector_store

    @property
    def search_engine(self) -> HybridSearchEngine:
        """Lazy-load search engine."""
        if self._search_engine is None:
            bm25_index = BM25Index(self.metadata_store)
            bm25_index.build_index()
            self._search_engine = HybridSearchEngine(
                embedder=self.embedder,
                metadata_store=self.metadata_store,
                vector_store=self.vector_store,
                bm25_index=bm25_index,
                top_k=self.config.retrieval.top_k,
            )
        return self._search_engine

    @property
    def memory_store(self) -> MemoryStore:
        """Lazy-load memory store."""
        if self._memory_store is None:
            self._memory_store = MemoryStore(self.config.data_dir)
        return self._memory_store

    def _setup_handlers(self) -> None:
        """Set up MCP tool handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="search_knowledge",
                    description="Search the knowledge base for relevant information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 5)",
                                "default": 5,
                            },
                            "source_type": {
                                "type": "string",
                                "description": "Filter by source type (e.g., 'markdown')",
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter by tags",
                            },
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="list_sources",
                    description="List all indexed sources in the knowledge base",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="get_stats",
                    description="Get statistics about the knowledge base",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="add_note",
                    description="Add a quick note to the knowledge base",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title of the note",
                            },
                            "content": {
                                "type": "string",
                                "description": "Content of the note",
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tags for the note",
                            },
                        },
                        "required": ["title", "content"],
                    },
                ),
                Tool(
                    name="ingest_content",
                    description="Ingest content from any source (GitHub, Notion, Slack, etc.) into the knowledge base. Use this to feed content from other MCP servers into Nexus for RAG.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title of the content",
                            },
                            "content": {
                                "type": "string",
                                "description": "The text content to index",
                            },
                            "source": {
                                "type": "string",
                                "description": "Source identifier (e.g., 'github:owner/repo', 'notion:page-id', 'slack:channel')",
                            },
                            "source_type": {
                                "type": "string",
                                "description": "Type of source: github, notion, slack, web, api, etc.",
                            },
                            "url": {
                                "type": "string",
                                "description": "Original URL of the content (if available)",
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tags to categorize the content",
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Additional metadata (author, date, etc.)",
                            },
                        },
                        "required": ["title", "content", "source"],
                    },
                ),
                Tool(
                    name="batch_ingest",
                    description="Ingest multiple documents at once from any source. Efficient for bulk imports from other MCP servers.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "documents": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "content": {"type": "string"},
                                        "source": {"type": "string"},
                                        "tags": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                        },
                                    },
                                    "required": ["title", "content", "source"],
                                },
                                "description": "Array of documents to ingest",
                            },
                            "source_type": {
                                "type": "string",
                                "description": "Type of source for all documents",
                            },
                        },
                        "required": ["documents"],
                    },
                ),
                # AI Memory Tools
                Tool(
                    name="remember",
                    description="Store something important for later. Use this to remember decisions, preferences, facts, or context about the current project.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "What to remember",
                            },
                            "memory_type": {
                                "type": "string",
                                "enum": ["decision", "preference", "context", "fact", "todo"],
                                "description": "Type of memory",
                                "default": "fact",
                            },
                            "project": {
                                "type": "string",
                                "description": "Project this relates to (optional)",
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tags for categorization",
                            },
                        },
                        "required": ["content"],
                    },
                ),
                Tool(
                    name="recall",
                    description="Recall memories matching criteria. Use this before answering questions to get relevant context.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Text to search for in memories",
                            },
                            "memory_type": {
                                "type": "string",
                                "enum": ["decision", "preference", "context", "fact", "todo"],
                                "description": "Filter by memory type",
                            },
                            "project": {
                                "type": "string",
                                "description": "Filter by project",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum results (default: 10)",
                                "default": 10,
                            },
                        },
                    },
                ),
                Tool(
                    name="get_project_context",
                    description="Get all context for a specific project - decisions, preferences, facts, and TODOs.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project": {
                                "type": "string",
                                "description": "Project name",
                            },
                        },
                        "required": ["project"],
                    },
                ),
                Tool(
                    name="forget",
                    description="Delete a memory by ID or matching criteria.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "memory_id": {
                                "type": "string",
                                "description": "Specific memory ID to delete",
                            },
                            "query": {
                                "type": "string",
                                "description": "Delete memories containing this text",
                            },
                            "project": {
                                "type": "string",
                                "description": "Delete all memories for this project",
                            },
                        },
                    },
                ),
                Tool(
                    name="get_user_preferences",
                    description="Get all stored user preferences.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Handle tool calls."""
            try:
                if name == "search_knowledge":
                    return await self._handle_search(arguments)
                elif name == "list_sources":
                    return await self._handle_list_sources()
                elif name == "get_stats":
                    return await self._handle_get_stats()
                elif name == "add_note":
                    return await self._handle_add_note(arguments)
                elif name == "ingest_content":
                    return await self._handle_ingest_content(arguments)
                elif name == "batch_ingest":
                    return await self._handle_batch_ingest(arguments)
                # AI Memory Tools
                elif name == "remember":
                    return await self._handle_remember(arguments)
                elif name == "recall":
                    return await self._handle_recall(arguments)
                elif name == "get_project_context":
                    return await self._handle_get_project_context(arguments)
                elif name == "forget":
                    return await self._handle_forget(arguments)
                elif name == "get_user_preferences":
                    return await self._handle_get_user_preferences()
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                logger.error(f"Tool error: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _handle_search(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle search_knowledge tool."""
        query = arguments["query"]
        limit = arguments.get("limit", 5)
        source_type = arguments.get("source_type")
        tags = arguments.get("tags")

        results = self.search_engine.search(
            query=query,
            top_k=limit,
            source_type=source_type,
            tags=tags,
        )

        if not results:
            return [TextContent(type="text", text="No results found.")]

        # Format results
        output_parts = [f"Found {len(results)} results:\n"]
        for i, r in enumerate(results, 1):
            source_info = f"[{r.source}]" if r.source else ""
            title_info = f" - {r.title}" if r.title else ""
            heading_info = f" > {r.heading}" if r.heading else ""
            score = f"({r.relevance_score:.3f})"

            output_parts.append(f"\n--- Result {i} {score} ---")
            output_parts.append(f"Source: {source_info}{title_info}{heading_info}")
            output_parts.append(f"Content:\n{r.content}\n")

        return [TextContent(type="text", text="\n".join(output_parts))]

    async def _handle_list_sources(self) -> list[TextContent]:
        """Handle list_sources tool."""
        sources = self.metadata_store.list_sources()

        if not sources:
            return [TextContent(type="text", text="No sources indexed.")]

        output_parts = [f"Indexed sources ({len(sources)}):\n"]
        for s in sources:
            output_parts.append(f"- {s.name}: {s.path} ({s.source_type})")

        return [TextContent(type="text", text="\n".join(output_parts))]

    async def _handle_get_stats(self) -> list[TextContent]:
        """Handle get_stats tool."""
        stats = self.metadata_store.get_stats()
        vector_count = self.vector_store.get_count()

        output = f"""Knowledge Base Statistics:
- Sources: {stats.get('sources', 0)}
- Documents: {stats.get('documents', 0)}
- Chunks: {stats.get('chunks', 0)}
- Vectors: {vector_count}"""

        return [TextContent(type="text", text=output)]

    async def _handle_add_note(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle add_note tool."""
        title = arguments["title"]
        content = arguments["content"]
        tags = arguments.get("tags", [])

        # Create a temporary markdown content
        frontmatter = f"""---
title: {title}
tags: {tags}
---

# {title}

{content}
"""
        # Save to notes directory
        notes_dir = self.config.notes_dir
        notes_dir.mkdir(parents=True, exist_ok=True)

        # Create filename from title
        import re
        safe_title = re.sub(r'[^\w\s-]', '', title.lower())
        safe_title = re.sub(r'[-\s]+', '-', safe_title).strip('-')
        note_path = notes_dir / f"{safe_title}.md"

        # Write note
        note_path.write_text(frontmatter)

        # Ingest note
        if self._pipeline is None:
            self._pipeline = IngestionPipeline(
                embedder=self.embedder,
                metadata_store=self.metadata_store,
                vector_store=self.vector_store,
            )

        doc = self._pipeline.ingest_file(note_path)

        if doc:
            # Rebuild BM25 index
            if self._search_engine:
                self._search_engine.build_bm25_index()

            return [TextContent(
                type="text",
                text=f"Note '{title}' added successfully with {len(doc.chunks)} chunks.",
            )]
        else:
            return [TextContent(type="text", text=f"Note '{title}' saved but already exists.")]

    async def _handle_ingest_content(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle ingest_content tool - ingest content from any MCP source."""
        title = arguments["title"]
        content = arguments["content"]
        source = arguments["source"]
        source_type = arguments.get("source_type", "mcp")
        url = arguments.get("url", "")
        tags = arguments.get("tags", [])
        metadata = arguments.get("metadata", {})

        # Create markdown content with frontmatter
        import json
        from datetime import datetime

        frontmatter = f"""---
title: {title}
source: {source}
source_type: {source_type}
url: {url}
tags: {tags}
ingested_at: {datetime.now().isoformat()}
metadata: {json.dumps(metadata)}
---

# {title}

{content}
"""
        # Save to ingested directory
        ingested_dir = self.config.data_dir / "ingested" / source_type
        ingested_dir.mkdir(parents=True, exist_ok=True)

        # Create safe filename
        import re
        safe_title = re.sub(r'[^\w\s-]', '', title.lower())
        safe_title = re.sub(r'[-\s]+', '-', safe_title).strip('-')[:50]
        import hashlib
        source_hash = hashlib.md5(source.encode()).hexdigest()[:8]
        file_path = ingested_dir / f"{safe_title}-{source_hash}.md"

        # Write content
        file_path.write_text(frontmatter)

        # Ingest into knowledge base
        if self._pipeline is None:
            self._pipeline = IngestionPipeline(
                embedder=self.embedder,
                metadata_store=self.metadata_store,
                vector_store=self.vector_store,
            )

        doc = self._pipeline.ingest_file(file_path)

        if doc:
            # Rebuild BM25 index
            if self._search_engine:
                self._search_engine.build_bm25_index()

            return [TextContent(
                type="text",
                text=f"Ingested '{title}' from {source} ({source_type}): {len(doc.chunks)} chunks indexed.",
            )]
        else:
            return [TextContent(type="text", text=f"Content '{title}' already exists.")]

    async def _handle_batch_ingest(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle batch_ingest tool - ingest multiple documents at once."""
        documents = arguments["documents"]
        source_type = arguments.get("source_type", "mcp")

        if not documents:
            return [TextContent(type="text", text="No documents provided.")]

        # Ingest each document
        success_count = 0
        total_chunks = 0
        errors = []

        for doc_data in documents:
            try:
                result = await self._handle_ingest_content({
                    "title": doc_data["title"],
                    "content": doc_data["content"],
                    "source": doc_data["source"],
                    "source_type": source_type,
                    "tags": doc_data.get("tags", []),
                })
                if "chunks indexed" in result[0].text:
                    success_count += 1
                    # Extract chunk count
                    import re
                    match = re.search(r'(\d+) chunks', result[0].text)
                    if match:
                        total_chunks += int(match.group(1))
            except Exception as e:
                errors.append(f"{doc_data.get('title', 'Unknown')}: {str(e)}")

        # Summary
        summary = f"Batch ingest complete: {success_count}/{len(documents)} documents, {total_chunks} total chunks."
        if errors:
            summary += f"\nErrors ({len(errors)}):\n" + "\n".join(errors[:5])

        return [TextContent(type="text", text=summary)]

    # ========== AI Memory Handlers ==========

    async def _handle_remember(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle remember tool - store a memory."""
        content = arguments["content"]
        memory_type = arguments.get("memory_type", "fact")
        project = arguments.get("project")
        tags = arguments.get("tags", [])

        memory_id = self.memory_store.remember(
            content=content,
            memory_type=memory_type,
            project=project,
            tags=tags,
        )

        return [TextContent(
            type="text",
            text=f"Remembered ({memory_type}): {content[:100]}... [ID: {memory_id}]",
        )]

    async def _handle_recall(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle recall tool - retrieve memories."""
        query = arguments.get("query")
        memory_type = arguments.get("memory_type")
        project = arguments.get("project")
        limit = arguments.get("limit", 10)

        memories = self.memory_store.recall(
            query=query,
            memory_type=memory_type,
            project=project,
            limit=limit,
        )

        if not memories:
            return [TextContent(type="text", text="No memories found matching criteria.")]

        output_parts = [f"Found {len(memories)} memories:\n"]
        for m in memories:
            project_str = f" [{m.get('project')}]" if m.get('project') else ""
            tags_str = f" #{' #'.join(m.get('tags', []))}" if m.get('tags') else ""
            output_parts.append(
                f"- [{m['type']}]{project_str}: {m['content'][:150]}{tags_str}"
            )

        return [TextContent(type="text", text="\n".join(output_parts))]

    async def _handle_get_project_context(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle get_project_context tool."""
        project = arguments["project"]
        context = self.memory_store.get_project_context(project)

        output = f"Project Context: {project}\n\n"

        if context["decisions"]:
            output += "📋 Decisions:\n" + "\n".join(f"  - {d}" for d in context["decisions"]) + "\n\n"
        if context["preferences"]:
            output += "⚙️ Preferences:\n" + "\n".join(f"  - {p}" for p in context["preferences"]) + "\n\n"
        if context["facts"]:
            output += "📝 Facts:\n" + "\n".join(f"  - {f}" for f in context["facts"]) + "\n\n"
        if context["todos"]:
            output += "✅ TODOs:\n" + "\n".join(f"  - {t}" for t in context["todos"]) + "\n\n"

        if not any([context["decisions"], context["preferences"], context["facts"], context["todos"]]):
            output += "No memories stored for this project yet."

        return [TextContent(type="text", text=output)]

    async def _handle_forget(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle forget tool - delete memories."""
        memory_id = arguments.get("memory_id")
        query = arguments.get("query")
        project = arguments.get("project")

        if memory_id:
            success = self.memory_store.forget(memory_id)
            if success:
                return [TextContent(type="text", text=f"Forgot memory {memory_id}")]
            return [TextContent(type="text", text=f"Memory {memory_id} not found")]

        if query or project:
            count = self.memory_store.forget_by_query(query=query, project=project)
            return [TextContent(type="text", text=f"Forgot {count} memories")]

        return [TextContent(type="text", text="No criteria specified for deletion")]

    async def _handle_get_user_preferences(self) -> list[TextContent]:
        """Handle get_user_preferences tool."""
        preferences = self.memory_store.get_user_preferences()

        if not preferences:
            return [TextContent(type="text", text="No user preferences stored yet.")]

        output = "User Preferences:\n" + "\n".join(f"  - {p}" for p in preferences)
        return [TextContent(type="text", text=output)]

    async def run_stdio(self) -> None:
        """Run server with stdio transport."""
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="nexus",
                    server_version="0.1.0",
                ),
            )

    def close(self) -> None:
        """Close server resources."""
        if self._metadata_store:
            self._metadata_store.close()
        if self._vector_store:
            self._vector_store.close()


def run_server(config_path: Path | None = None) -> None:
    """Run the Nexus MCP server."""
    server = NexusServer(config_path=config_path)
    try:
        asyncio.run(server.run_stdio())
    finally:
        server.close()


if __name__ == "__main__":
    run_server()
