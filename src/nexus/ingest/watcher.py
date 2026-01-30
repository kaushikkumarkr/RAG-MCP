"""File watcher for auto-indexing."""

import time
from pathlib import Path
from typing import Callable

from loguru import logger

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent, FileDeletedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = object


class MarkdownHandler(FileSystemEventHandler):
    """Handle markdown file changes."""

    def __init__(
        self,
        on_created: Callable[[Path], None] | None = None,
        on_modified: Callable[[Path], None] | None = None,
        on_deleted: Callable[[Path], None] | None = None,
        extensions: list[str] | None = None,
    ) -> None:
        """Initialize handler.
        
        Args:
            on_created: Callback for new files
            on_modified: Callback for modified files
            on_deleted: Callback for deleted files
            extensions: File extensions to watch (default: ['.md'])
        """
        self.on_created = on_created
        self.on_modified = on_modified
        self.on_deleted = on_deleted
        self.extensions = extensions or [".md"]
        self._last_event: dict[str, float] = {}
        self._debounce_seconds = 1.0

    def _should_handle(self, path: Path) -> bool:
        """Check if file should be handled."""
        return path.suffix.lower() in self.extensions

    def _debounce(self, path: str) -> bool:
        """Debounce rapid events on same file."""
        now = time.time()
        last = self._last_event.get(path, 0)
        if now - last < self._debounce_seconds:
            return False
        self._last_event[path] = now
        return True

    def on_created(self, event):
        """Handle file creation."""
        if event.is_directory:
            return
        path = Path(event.src_path)
        if self._should_handle(path) and self._debounce(str(path)):
            logger.info(f"File created: {path}")
            if self.on_created:
                self.on_created(path)

    def on_modified(self, event):
        """Handle file modification."""
        if event.is_directory:
            return
        path = Path(event.src_path)
        if self._should_handle(path) and self._debounce(str(path)):
            logger.info(f"File modified: {path}")
            if self.on_modified:
                self.on_modified(path)

    def on_deleted(self, event):
        """Handle file deletion."""
        if event.is_directory:
            return
        path = Path(event.src_path)
        if self._should_handle(path):
            logger.info(f"File deleted: {path}")
            if self.on_deleted:
                self.on_deleted(path)


class FileWatcher:
    """Watch directories for file changes."""

    def __init__(self) -> None:
        """Initialize watcher."""
        if not WATCHDOG_AVAILABLE:
            raise ImportError("watchdog not installed. Run: pip install watchdog")
        self.observer = Observer()
        self._handlers: dict[str, MarkdownHandler] = {}

    def watch(
        self,
        directory: Path,
        on_created: Callable[[Path], None] | None = None,
        on_modified: Callable[[Path], None] | None = None,
        on_deleted: Callable[[Path], None] | None = None,
        recursive: bool = True,
    ) -> None:
        """Start watching a directory.
        
        Args:
            directory: Directory to watch
            on_created: Callback for new files
            on_modified: Callback for modified files
            on_deleted: Callback for deleted files
            recursive: Watch subdirectories
        """
        handler = MarkdownHandler(
            on_created=on_created,
            on_modified=on_modified,
            on_deleted=on_deleted,
        )
        self.observer.schedule(handler, str(directory), recursive=recursive)
        self._handlers[str(directory)] = handler
        logger.info(f"Watching {directory} (recursive={recursive})")

    def start(self) -> None:
        """Start the watcher."""
        self.observer.start()
        logger.info("File watcher started")

    def stop(self) -> None:
        """Stop the watcher."""
        self.observer.stop()
        self.observer.join()
        logger.info("File watcher stopped")

    def run_forever(self) -> None:
        """Run watcher until interrupted."""
        self.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
