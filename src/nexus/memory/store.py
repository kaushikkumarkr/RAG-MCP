"""Memory layer for AI assistants - fast context retrieval and storage."""

from datetime import datetime
from pathlib import Path
from typing import Any
import json

from loguru import logger

from nexus.storage.metadata import MetadataStore
from nexus.models.document import Document, Chunk


class MemoryType:
    """Types of memories for categorization."""
    DECISION = "decision"       # Architecture/design decisions
    PREFERENCE = "preference"   # User preferences
    CONTEXT = "context"         # Project context
    FACT = "fact"               # Learned facts
    CONVERSATION = "conversation"  # Conversation summaries
    TODO = "todo"               # Things to remember to do


class MemoryStore:
    """Fast memory storage for AI context."""

    def __init__(self, data_dir: Path) -> None:
        """Initialize memory store.
        
        Args:
            data_dir: Directory for memory storage
        """
        self.data_dir = data_dir
        self.memories_dir = data_dir / "memories"
        self.memories_dir.mkdir(parents=True, exist_ok=True)
        
        # Fast in-memory index for quick lookups
        self._index: dict[str, dict[str, Any]] = {}
        self._load_index()

    def _index_path(self) -> Path:
        """Get path to memory index."""
        return self.memories_dir / "index.json"

    def _load_index(self) -> None:
        """Load memory index from disk."""
        index_path = self._index_path()
        if index_path.exists():
            try:
                self._index = json.loads(index_path.read_text())
            except Exception as e:
                logger.warning(f"Failed to load memory index: {e}")
                self._index = {}

    def _save_index(self) -> None:
        """Save memory index to disk."""
        self._index_path().write_text(json.dumps(self._index, indent=2, default=str))

    def remember(
        self,
        content: str,
        memory_type: str = MemoryType.FACT,
        project: str | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Store a memory for later recall.
        
        Args:
            content: The content to remember
            memory_type: Type of memory (decision, preference, context, fact)
            project: Project this memory belongs to
            tags: Tags for categorization
            metadata: Additional metadata
            
        Returns:
            Memory ID
        """
        import hashlib
        
        # Generate unique ID
        timestamp = datetime.now().isoformat()
        memory_id = hashlib.md5(f"{content}{timestamp}".encode()).hexdigest()[:12]
        
        memory = {
            "id": memory_id,
            "content": content,
            "type": memory_type,
            "project": project,
            "tags": tags or [],
            "metadata": metadata or {},
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        
        # Store in index
        self._index[memory_id] = memory
        self._save_index()
        
        # Also save as individual file for persistence
        memory_file = self.memories_dir / f"{memory_id}.json"
        memory_file.write_text(json.dumps(memory, indent=2, default=str))
        
        logger.debug(f"Remembered: {memory_id} ({memory_type})")
        return memory_id

    def recall(
        self,
        query: str | None = None,
        memory_type: str | None = None,
        project: str | None = None,
        tags: list[str] | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Recall memories matching criteria.
        
        Args:
            query: Text to search for in content
            memory_type: Filter by memory type
            project: Filter by project
            tags: Filter by tags (any match)
            limit: Maximum results
            
        Returns:
            List of matching memories
        """
        results = []
        
        for memory in self._index.values():
            # Apply filters
            if memory_type and memory.get("type") != memory_type:
                continue
            if project and memory.get("project") != project:
                continue
            if tags and not any(t in memory.get("tags", []) for t in tags):
                continue
            if query and query.lower() not in memory.get("content", "").lower():
                continue
            
            results.append(memory)
        
        # Sort by recency
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return results[:limit]

    def get_project_context(self, project: str) -> dict[str, Any]:
        """Get all context for a project.
        
        Args:
            project: Project name
            
        Returns:
            Dictionary with project context organized by type
        """
        context = {
            "project": project,
            "decisions": [],
            "preferences": [],
            "facts": [],
            "todos": [],
        }
        
        for memory in self._index.values():
            if memory.get("project") != project:
                continue
            
            memory_type = memory.get("type", "fact")
            if memory_type == MemoryType.DECISION:
                context["decisions"].append(memory["content"])
            elif memory_type == MemoryType.PREFERENCE:
                context["preferences"].append(memory["content"])
            elif memory_type == MemoryType.TODO:
                context["todos"].append(memory["content"])
            else:
                context["facts"].append(memory["content"])
        
        return context

    def get_user_preferences(self) -> list[str]:
        """Get all user preferences.
        
        Returns:
            List of preference strings
        """
        preferences = self.recall(memory_type=MemoryType.PREFERENCE, limit=50)
        return [p["content"] for p in preferences]

    def update_memory(
        self,
        memory_id: str,
        content: str | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Update an existing memory.
        
        Args:
            memory_id: ID of memory to update
            content: New content (if updating)
            tags: New tags (if updating)
            metadata: Additional metadata to merge
            
        Returns:
            True if updated, False if not found
        """
        if memory_id not in self._index:
            return False
        
        memory = self._index[memory_id]
        
        if content is not None:
            memory["content"] = content
        if tags is not None:
            memory["tags"] = tags
        if metadata:
            memory["metadata"].update(metadata)
        
        memory["updated_at"] = datetime.now().isoformat()
        
        self._save_index()
        
        # Update file
        memory_file = self.memories_dir / f"{memory_id}.json"
        memory_file.write_text(json.dumps(memory, indent=2, default=str))
        
        return True

    def forget(self, memory_id: str) -> bool:
        """Delete a memory.
        
        Args:
            memory_id: ID of memory to delete
            
        Returns:
            True if deleted, False if not found
        """
        if memory_id not in self._index:
            return False
        
        del self._index[memory_id]
        self._save_index()
        
        # Delete file
        memory_file = self.memories_dir / f"{memory_id}.json"
        if memory_file.exists():
            memory_file.unlink()
        
        return True

    def forget_by_query(
        self,
        query: str | None = None,
        memory_type: str | None = None,
        project: str | None = None,
    ) -> int:
        """Delete memories matching criteria.
        
        Args:
            query: Text to match in content
            memory_type: Filter by type
            project: Filter by project
            
        Returns:
            Number of memories deleted
        """
        to_delete = self.recall(query=query, memory_type=memory_type, project=project, limit=1000)
        
        deleted = 0
        for memory in to_delete:
            if self.forget(memory["id"]):
                deleted += 1
        
        return deleted

    def get_recent(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get most recent memories.
        
        Args:
            limit: Maximum results
            
        Returns:
            List of recent memories
        """
        memories = list(self._index.values())
        memories.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return memories[:limit]

    def list_projects(self) -> list[str]:
        """List all projects with memories.
        
        Returns:
            List of project names
        """
        projects = set()
        for memory in self._index.values():
            if memory.get("project"):
                projects.add(memory["project"])
        return sorted(projects)

    def get_stats(self) -> dict[str, Any]:
        """Get memory statistics.
        
        Returns:
            Statistics dictionary
        """
        stats = {
            "total_memories": len(self._index),
            "by_type": {},
            "by_project": {},
        }
        
        for memory in self._index.values():
            # Count by type
            mtype = memory.get("type", "unknown")
            stats["by_type"][mtype] = stats["by_type"].get(mtype, 0) + 1
            
            # Count by project
            project = memory.get("project", "none")
            stats["by_project"][project] = stats["by_project"].get(project, 0) + 1
        
        return stats
