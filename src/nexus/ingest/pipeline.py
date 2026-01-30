"""Document ingestion pipeline."""

import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from nexus.config import Config
from nexus.exceptions import IngestionError
from nexus.ingest.chunker import ChunkInfo, TextChunker
from nexus.ingest.loader import MarkdownLoader, ParsedDocument
from nexus.models.document import Chunk, ChunkMetadata, Document
from nexus.models.source import Source, SourceType
from nexus.rag.embedder import Embedder
from nexus.storage.metadata import MetadataStore
from nexus.storage.vectors import VectorStore


class IngestionPipeline:
    """Pipeline for ingesting documents into the knowledge base."""

    def __init__(
        self,
        embedder: Embedder,
        metadata_store: MetadataStore,
        vector_store: VectorStore,
        chunker: TextChunker | None = None,
        loader: MarkdownLoader | None = None,
    ) -> None:
        """Initialize ingestion pipeline.

        Args:
            embedder: Embedding service
            metadata_store: Metadata storage
            vector_store: Vector storage
            chunker: Text chunker (default: TextChunker())
            loader: Markdown loader (default: MarkdownLoader())
        """
        self.embedder = embedder
        self.metadata_store = metadata_store
        self.vector_store = vector_store
        self.chunker = chunker or TextChunker()
        self.loader = loader or MarkdownLoader()

    def ingest_file(self, path: Path) -> Document | None:
        """Ingest a single file.

        Args:
            path: Path to file

        Returns:
            Ingested document or None if skipped
        """
        # Compute content hash
        content = path.read_text(encoding="utf-8")
        content_hash = hashlib.md5(content.encode()).hexdigest()

        # Check if already indexed
        if self.metadata_store.document_exists(str(path), content_hash):
            logger.debug(f"Skipping unchanged file: {path}")
            return None

        # Parse document
        parsed = self.loader.parse(content)

        # Create document
        doc_id = str(uuid.uuid4())
        doc = Document(
            id=doc_id,
            source_path=str(path),
            source_type="markdown",
            title=parsed.title,
            content=parsed.content,
            content_hash=content_hash,
            metadata=parsed.metadata,
        )

        # Chunk document
        chunk_infos = self.chunker.chunk_text(parsed.content, parsed.headings)

        # Create chunk objects
        chunks: list[Chunk] = []
        for i, chunk_info in enumerate(chunk_infos):
            chunk_id = f"{doc_id}-chunk-{i}"
            chunk = Chunk(
                id=chunk_id,
                document_id=doc_id,
                content=chunk_info.content,
                chunk_index=i,
                metadata=ChunkMetadata(
                    source_path=str(path),
                    source_type="markdown",
                    start_line=chunk_info.start_line,
                    end_line=chunk_info.end_line,
                    heading=chunk_info.heading,
                    tags=parsed.tags,
                    title=parsed.title,
                    author=parsed.author,
                    created_at=parsed.created_at,
                ),
            )
            chunks.append(chunk)

        doc.chunks = chunks

        # Generate embeddings
        texts = [c.content for c in chunks]
        embeddings = self.embedder.embed_texts(texts)

        # Store in metadata DB
        self.metadata_store.add_document(doc)
        for chunk in chunks:
            self.metadata_store.add_chunk(chunk)

        # Store vectors
        chunk_ids = [c.id for c in chunks]
        payloads = [
            {
                "source_path": c.metadata.source_path,
                "source_type": c.metadata.source_type,
                "heading": c.metadata.heading,
                "title": c.metadata.title,
                "tags": c.metadata.tags,
            }
            for c in chunks
        ]
        self.vector_store.add_vectors(chunk_ids, embeddings, payloads)

        logger.info(f"Ingested {path}: {len(chunks)} chunks")
        return doc

    def ingest_directory(
        self,
        directory: Path,
        recursive: bool = True,
    ) -> list[Document]:
        """Ingest all markdown files in a directory.

        Args:
            directory: Directory to ingest
            recursive: Whether to recurse into subdirectories

        Returns:
            List of ingested documents
        """
        docs: list[Document] = []

        glob_func = directory.rglob if recursive else directory.glob
        paths = sorted(glob_func("*.md"))

        for path in paths:
            if path.is_file():
                try:
                    doc = self.ingest_file(path)
                    if doc:
                        docs.append(doc)
                except Exception as e:
                    logger.warning(f"Failed to ingest {path}: {e}")

        logger.info(f"Ingested {len(docs)} documents from {directory}")
        return docs

    def delete_document(self, doc_id: str) -> None:
        """Delete a document and its chunks.

        Args:
            doc_id: Document ID to delete
        """
        # Get chunks for this document
        chunks = self.metadata_store.get_chunks_by_document(doc_id)
        chunk_ids = [c.id for c in chunks]

        # Delete from vector store
        if chunk_ids:
            self.vector_store.delete_vectors(chunk_ids)

        # Delete from metadata store
        self.metadata_store.delete_document(doc_id)

        logger.info(f"Deleted document {doc_id} with {len(chunk_ids)} chunks")
