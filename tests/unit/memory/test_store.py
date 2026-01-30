"""Tests for MemoryStore."""

import shutil
from pathlib import Path
import pytest
from nexus.memory.store import MemoryStore, MemoryType

@pytest.fixture
def memory_store(tmp_path):
    """Create a temporary memory store."""
    store = MemoryStore(tmp_path)
    yield store
    # Cleanup handled by tmp_path

def test_remember_recall(memory_store):
    """Test storage and retrieval."""
    # Remember
    mem_id = memory_store.remember(
        content="User likes Python",
        memory_type=MemoryType.PREFERENCE,
        project="nexus-test",
        tags=["coding", "python"]
    )
    assert mem_id is not None

    # Recall
    memories = memory_store.recall(project="nexus-test")
    assert len(memories) == 1
    assert memories[0]["content"] == "User likes Python"
    assert memories[0]["type"] == MemoryType.PREFERENCE

def test_get_context(memory_store):
    """Test context retrieval."""
    memory_store.remember("Use Postgres", MemoryType.DECISION, "project-a")
    memory_store.remember("Dark mode", MemoryType.PREFERENCE, "project-a")
    memory_store.remember("API is ready", MemoryType.FACT, "project-a")
    memory_store.remember("Implement login", MemoryType.TODO, "project-a")

    context = memory_store.get_project_context("project-a")
    
    assert len(context["decisions"]) == 1
    assert len(context["preferences"]) == 1
    assert len(context["facts"]) == 1
    assert len(context["todos"]) == 1
    assert context["decisions"][0] == "Use Postgres"

def test_forget(memory_store):
    """Test deletion."""
    mem_id = memory_store.remember("Secret", MemoryType.FACT)
    assert len(memory_store.recall()) == 1
    
    assert memory_store.forget(mem_id) is True
    assert len(memory_store.recall()) == 0

def test_update(memory_store):
    """Test updating memories."""
    mem_id = memory_store.remember("Old content")
    
    success = memory_store.update_memory(
        mem_id, 
        content="New content",
        tags=["updated"]
    )
    
    assert success is True
    memories = memory_store.recall()
    assert memories[0]["content"] == "New content"
    assert "updated" in memories[0]["tags"]
