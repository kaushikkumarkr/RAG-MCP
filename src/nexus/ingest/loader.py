"""Markdown loader with frontmatter parsing."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from loguru import logger

from nexus.exceptions import IngestionError


@dataclass
class ParsedDocument:
    """Result of parsing a markdown document."""

    content: str
    title: str | None = None
    tags: list[str] = field(default_factory=list)
    author: str | None = None
    created_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    headings: list[tuple[int, str, int]] = field(default_factory=list)  # (level, text, line)


class MarkdownLoader:
    """Load and parse markdown files with frontmatter."""

    FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    def load_file(self, path: Path) -> ParsedDocument:
        """Load and parse a markdown file.

        Args:
            path: Path to markdown file

        Returns:
            ParsedDocument with content and metadata
        """
        if not path.exists():
            raise IngestionError(f"File not found: {path}")

        try:
            content = path.read_text(encoding="utf-8")
            return self.parse(content)
        except UnicodeDecodeError as e:
            raise IngestionError(f"Failed to read file {path}: {e}") from e

    def parse(self, content: str) -> ParsedDocument:
        """Parse markdown content.

        Args:
            content: Raw markdown content

        Returns:
            ParsedDocument with content and metadata
        """
        # Extract frontmatter
        frontmatter: dict[str, Any] = {}
        body = content

        match = self.FRONTMATTER_PATTERN.match(content)
        if match:
            try:
                frontmatter = yaml.safe_load(match.group(1)) or {}
                body = content[match.end() :]
            except yaml.YAMLError as e:
                logger.warning(f"Failed to parse frontmatter: {e}")

        # Extract headings
        headings: list[tuple[int, str, int]] = []
        for i, line in enumerate(body.split("\n"), start=1):
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2).strip()
                headings.append((level, text, i))

        # Extract metadata
        title = frontmatter.get("title")
        if not title and headings:
            # Use first h1 as title
            h1s = [(text, line) for level, text, line in headings if level == 1]
            if h1s:
                title = h1s[0][0]

        tags = frontmatter.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]

        created_at = None
        date_str = frontmatter.get("date") or frontmatter.get("created")
        if date_str:
            try:
                if isinstance(date_str, datetime):
                    created_at = date_str
                else:
                    created_at = datetime.fromisoformat(str(date_str))
            except ValueError:
                pass

        return ParsedDocument(
            content=body.strip(),
            title=title,
            tags=tags,
            author=frontmatter.get("author"),
            created_at=created_at,
            metadata={k: v for k, v in frontmatter.items() if k not in ("title", "tags", "author", "date", "created")},
            headings=headings,
        )

    def load_directory(
        self,
        directory: Path,
        recursive: bool = True,
        pattern: str = "*.md",
    ) -> list[tuple[Path, ParsedDocument]]:
        """Load all markdown files from a directory.

        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories
            pattern: Glob pattern for files

        Returns:
            List of (path, parsed_document) tuples
        """
        if not directory.exists():
            raise IngestionError(f"Directory not found: {directory}")

        results: list[tuple[Path, ParsedDocument]] = []
        glob_func = directory.rglob if recursive else directory.glob

        for path in sorted(glob_func(pattern)):
            if path.is_file():
                try:
                    doc = self.load_file(path)
                    results.append((path, doc))
                except IngestionError as e:
                    logger.warning(f"Skipping {path}: {e}")

        logger.info(f"Loaded {len(results)} documents from {directory}")
        return results
