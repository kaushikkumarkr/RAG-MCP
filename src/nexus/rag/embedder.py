"""Embedding service using sentence-transformers."""

from typing import Any

from loguru import logger
from sentence_transformers import SentenceTransformer

from nexus.exceptions import NexusError


class Embedder:
    """Embedding service using sentence-transformers."""

    def __init__(
        self,
        model_name: str = "BAAI/bge-base-en-v1.5",
        batch_size: int = 32,
        normalize: bool = True,
        device: str | None = None,
    ) -> None:
        """Initialize embedder.

        Args:
            model_name: Name of the sentence-transformers model
            batch_size: Batch size for encoding
            normalize: Whether to normalize embeddings
            device: Device to use (mps, cuda, cpu, or None for auto)
        """
        self.model_name = model_name
        self.batch_size = batch_size
        self.normalize = normalize
        self._model: SentenceTransformer | None = None
        self._device = device
        self._dimension: int | None = None

    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the model."""
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name, device=self._device)
            self._dimension = self._model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded. Dimension: {self._dimension}")
        return self._model

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        if self._dimension is None:
            # Force model load to get dimension
            _ = self.model
        return self._dimension  # type: ignore

    def embed_text(self, text: str) -> list[float]:
        """Embed a single text string.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        embedding = self.model.encode(
            text,
            normalize_embeddings=self.normalize,
            show_progress_bar=False,
        )
        return embedding.tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=self.normalize,
            show_progress_bar=len(texts) > 100,
        )
        return embeddings.tolist()

    def similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Cosine similarity score (0-1)
        """
        emb1 = self.embed_text(text1)
        emb2 = self.embed_text(text2)

        # Compute cosine similarity (embeddings are normalized)
        dot_product = sum(a * b for a, b in zip(emb1, emb2))
        return dot_product
