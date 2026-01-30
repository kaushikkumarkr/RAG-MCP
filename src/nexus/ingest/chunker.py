"""Text chunking strategies."""

import re
from dataclasses import dataclass
from typing import Iterator

from loguru import logger


@dataclass
class ChunkInfo:
    """Information about a chunk."""

    content: str
    start_line: int
    end_line: int
    heading: str | None = None


class TextChunker:
    """Chunk text into semantic segments."""

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        min_chunk_size: int = 100,
    ) -> None:
        """Initialize chunker.

        Args:
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks
            min_chunk_size: Minimum chunk size
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    def chunk_text(
        self,
        text: str,
        headings: list[tuple[int, str, int]] | None = None,
    ) -> list[ChunkInfo]:
        """Chunk text into semantic segments.

        Uses a hierarchical approach:
        1. First split by sections (headings)
        2. Then split large sections by paragraphs
        3. Finally split large paragraphs by sentences

        Args:
            text: Text to chunk
            headings: Optional list of (level, text, line) tuples

        Returns:
            List of ChunkInfo objects
        """
        lines = text.split("\n")
        chunks: list[ChunkInfo] = []

        # If no headings, chunk by paragraphs
        if not headings:
            return self._chunk_by_paragraphs(text)

        # Sort headings by line number
        sorted_headings = sorted(headings, key=lambda h: h[2])

        # Create sections between headings
        sections: list[tuple[int, int, str | None]] = []  # (start_line, end_line, heading)

        for i, (level, heading_text, line_num) in enumerate(sorted_headings):
            # Find end of this section (start of next heading or end of document)
            if i + 1 < len(sorted_headings):
                end_line = sorted_headings[i + 1][2] - 1
            else:
                end_line = len(lines)

            sections.append((line_num, end_line, heading_text))

        # Add any content before first heading
        if sorted_headings and sorted_headings[0][2] > 1:
            sections.insert(0, (1, sorted_headings[0][2] - 1, None))

        # Chunk each section
        for start_line, end_line, heading in sections:
            section_lines = lines[start_line - 1 : end_line]
            section_text = "\n".join(section_lines)

            if len(section_text) <= self.chunk_size:
                if len(section_text.strip()) >= self.min_chunk_size:
                    chunks.append(
                        ChunkInfo(
                            content=section_text.strip(),
                            start_line=start_line,
                            end_line=end_line,
                            heading=heading,
                        )
                    )
            else:
                # Further chunk large sections
                sub_chunks = self._chunk_large_text(
                    section_text, start_line, heading
                )
                chunks.extend(sub_chunks)

        return chunks

    def _chunk_by_paragraphs(self, text: str) -> list[ChunkInfo]:
        """Chunk text by paragraphs when no headings are available."""
        paragraphs = re.split(r"\n\s*\n", text)
        chunks: list[ChunkInfo] = []
        current_chunk = ""
        current_start = 1
        line_count = 1

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_lines = para.count("\n") + 1

            if len(current_chunk) + len(para) <= self.chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
                    current_start = line_count
            else:
                # Save current chunk
                if len(current_chunk) >= self.min_chunk_size:
                    chunks.append(
                        ChunkInfo(
                            content=current_chunk,
                            start_line=current_start,
                            end_line=line_count - 1,
                            heading=None,
                        )
                    )
                current_chunk = para
                current_start = line_count

            line_count += para_lines + 1  # +1 for blank line

        # Add final chunk
        if current_chunk and len(current_chunk) >= self.min_chunk_size:
            chunks.append(
                ChunkInfo(
                    content=current_chunk,
                    start_line=current_start,
                    end_line=line_count,
                    heading=None,
                )
            )

        return chunks

    def _chunk_large_text(
        self,
        text: str,
        start_line: int,
        heading: str | None,
    ) -> list[ChunkInfo]:
        """Chunk large text by sentences with overlap."""
        # Split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks: list[ChunkInfo] = []

        current_chunk = ""
        chunk_start = start_line

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += (" " if current_chunk else "") + sentence
            else:
                if len(current_chunk) >= self.min_chunk_size:
                    chunks.append(
                        ChunkInfo(
                            content=current_chunk.strip(),
                            start_line=chunk_start,
                            end_line=chunk_start + current_chunk.count("\n"),
                            heading=heading,
                        )
                    )

                # Start new chunk with overlap
                overlap_text = self._get_overlap(current_chunk)
                current_chunk = overlap_text + sentence
                chunk_start += current_chunk.count("\n")

        # Add final chunk
        if current_chunk and len(current_chunk) >= self.min_chunk_size:
            chunks.append(
                ChunkInfo(
                    content=current_chunk.strip(),
                    start_line=chunk_start,
                    end_line=chunk_start + current_chunk.count("\n"),
                    heading=heading,
                )
            )

        return chunks

    def _get_overlap(self, text: str) -> str:
        """Get overlap text from end of chunk."""
        if len(text) <= self.chunk_overlap:
            return text + " "

        # Try to get overlap at sentence boundary
        sentences = re.split(r"(?<=[.!?])\s+", text)
        overlap = ""
        for sentence in reversed(sentences):
            if len(overlap) + len(sentence) <= self.chunk_overlap:
                overlap = sentence + " " + overlap
            else:
                break

        return overlap if overlap else text[-self.chunk_overlap :] + " "
