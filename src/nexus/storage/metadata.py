"""SQLite metadata store for documents and sources."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from nexus.exceptions import StorageError
from nexus.models.document import Chunk, ChunkMetadata, Document
from nexus.models.source import Source, SourceType


class MetadataStore:
    """SQLite-based metadata storage for documents and chunks."""

    def __init__(self, db_path: Path) -> None:
        """Initialize metadata store.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._connection: sqlite3.Connection | None = None
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = self._get_connection()
        cursor = conn.cursor()

        # Sources table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                source_type TEXT NOT NULL,
                title TEXT,
                document_count INTEGER DEFAULT 0,
                chunk_count INTEGER DEFAULT 0,
                last_indexed TEXT,
                metadata TEXT
            )
        """)

        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                source_path TEXT NOT NULL,
                source_type TEXT NOT NULL,
                title TEXT,
                content_hash TEXT,
                indexed_at TEXT NOT NULL,
                metadata TEXT
            )
        """)

        # Chunks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                content TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                source_path TEXT NOT NULL,
                source_type TEXT NOT NULL,
                start_line INTEGER,
                end_line INTEGER,
                heading TEXT,
                tags TEXT,
                title TEXT,
                author TEXT,
                created_at TEXT,
                extra TEXT,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_document ON chunks(document_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_source ON documents(source_path)")

        conn.commit()
        logger.debug(f"Initialized metadata DB at {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(str(self.db_path))
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    # Source operations
    def add_source(self, source: Source) -> None:
        """Add a source to the database."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO sources
                (id, path, source_type, title, document_count, chunk_count, last_indexed, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source.id,
                    source.path,
                    source.source_type.value,
                    source.title,
                    source.document_count,
                    source.chunk_count,
                    source.last_indexed.isoformat() if source.last_indexed else None,
                    str(source.metadata),
                ),
            )
            conn.commit()
        except sqlite3.Error as e:
            raise StorageError(f"Failed to add source: {e}") from e

    def get_source(self, source_id: str) -> Source | None:
        """Get a source by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sources WHERE id = ?", (source_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return Source(
            id=row["id"],
            path=row["path"],
            source_type=SourceType(row["source_type"]),
            title=row["title"],
            document_count=row["document_count"],
            chunk_count=row["chunk_count"],
            last_indexed=datetime.fromisoformat(row["last_indexed"])
            if row["last_indexed"]
            else None,
        )

    def list_sources(self) -> list[Source]:
        """List all sources."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sources")
        rows = cursor.fetchall()

        return [
            Source(
                id=row["id"],
                path=row["path"],
                source_type=SourceType(row["source_type"]),
                title=row["title"],
                document_count=row["document_count"],
                chunk_count=row["chunk_count"],
                last_indexed=datetime.fromisoformat(row["last_indexed"])
                if row["last_indexed"]
                else None,
            )
            for row in rows
        ]

    def delete_source(self, source_id: str) -> None:
        """Delete a source and all its documents."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM sources WHERE id = ?", (source_id,))
        conn.commit()

    # Document operations
    def add_document(self, doc: Document) -> None:
        """Add a document to the database."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO documents
                (id, source_path, source_type, title, content_hash, indexed_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doc.id,
                    doc.source_path,
                    doc.source_type,
                    doc.title,
                    doc.content_hash,
                    doc.indexed_at.isoformat(),
                    str(doc.metadata),
                ),
            )
            conn.commit()
        except sqlite3.Error as e:
            raise StorageError(f"Failed to add document: {e}") from e

    def get_document(self, doc_id: str) -> Document | None:
        """Get a document by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return Document(
            id=row["id"],
            source_path=row["source_path"],
            source_type=row["source_type"],
            title=row["title"],
            content="",  # Content not stored in DB
            content_hash=row["content_hash"],
            indexed_at=datetime.fromisoformat(row["indexed_at"]),
        )

    def document_exists(self, source_path: str, content_hash: str) -> bool:
        """Check if a document with the same path and hash exists."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM documents WHERE source_path = ? AND content_hash = ?",
            (source_path, content_hash),
        )
        return cursor.fetchone() is not None

    def delete_document(self, doc_id: str) -> None:
        """Delete a document and its chunks."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM chunks WHERE document_id = ?", (doc_id,))
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()

    # Chunk operations
    def add_chunk(self, chunk: Chunk) -> None:
        """Add a chunk to the database."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO chunks
                (id, document_id, content, chunk_index, source_path, source_type,
                 start_line, end_line, heading, tags, title, author, created_at, extra)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk.id,
                    chunk.document_id,
                    chunk.content,
                    chunk.chunk_index,
                    chunk.metadata.source_path,
                    chunk.metadata.source_type,
                    chunk.metadata.start_line,
                    chunk.metadata.end_line,
                    chunk.metadata.heading,
                    ",".join(chunk.metadata.tags) if chunk.metadata.tags else None,
                    chunk.metadata.title,
                    chunk.metadata.author,
                    chunk.metadata.created_at.isoformat() if chunk.metadata.created_at else None,
                    str(chunk.metadata.extra) if chunk.metadata.extra else None,
                ),
            )
            conn.commit()
        except sqlite3.Error as e:
            raise StorageError(f"Failed to add chunk: {e}") from e

    def add_chunks(self, chunks: list[Chunk]) -> None:
        """Add multiple chunks to the database."""
        for chunk in chunks:
            self.add_chunk(chunk)

    def get_chunk(self, chunk_id: str) -> Chunk | None:
        """Get a chunk by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM chunks WHERE id = ?", (chunk_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_chunk(row)

    def get_chunks_by_document(self, doc_id: str) -> list[Chunk]:
        """Get all chunks for a document."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM chunks WHERE document_id = ? ORDER BY chunk_index", (doc_id,)
        )
        rows = cursor.fetchall()

        return [self._row_to_chunk(row) for row in rows]

    def get_chunks_by_ids(self, chunk_ids: list[str]) -> list[Chunk]:
        """Get multiple chunks by their IDs."""
        if not chunk_ids:
            return []

        conn = self._get_connection()
        cursor = conn.cursor()

        placeholders = ",".join("?" * len(chunk_ids))
        cursor.execute(f"SELECT * FROM chunks WHERE id IN ({placeholders})", chunk_ids)
        rows = cursor.fetchall()

        return [self._row_to_chunk(row) for row in rows]

    def _row_to_chunk(self, row: sqlite3.Row) -> Chunk:
        """Convert a database row to a Chunk object."""
        return Chunk(
            id=row["id"],
            document_id=row["document_id"],
            content=row["content"],
            chunk_index=row["chunk_index"],
            metadata=ChunkMetadata(
                source_path=row["source_path"],
                source_type=row["source_type"],
                start_line=row["start_line"],
                end_line=row["end_line"],
                heading=row["heading"],
                tags=row["tags"].split(",") if row["tags"] else [],
                title=row["title"],
                author=row["author"],
                created_at=datetime.fromisoformat(row["created_at"])
                if row["created_at"]
                else None,
            ),
        )

    def get_stats(self) -> dict[str, int]:
        """Get database statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()

        stats = {}

        cursor.execute("SELECT COUNT(*) FROM sources")
        stats["sources"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM documents")
        stats["documents"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM chunks")
        stats["chunks"] = cursor.fetchone()[0]

        return stats
