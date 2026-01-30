"""Cross-encoder reranker for better retrieval quality."""

from typing import Any

from loguru import logger


class CrossEncoderReranker:
    """Cross-encoder reranker using sentence-transformers."""

    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-base",
    ) -> None:
        """Initialize cross-encoder reranker.
        
        Args:
            model_name: Cross-encoder model name
        """
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        """Lazy-load the cross-encoder model."""
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
                logger.info(f"Loading cross-encoder: {self.model_name}")
                self._model = CrossEncoder(self.model_name)
                logger.info("Cross-encoder loaded")
            except Exception as e:
                logger.warning(f"Could not load cross-encoder: {e}")
                self._model = None
        return self._model

    def rerank(
        self,
        query: str,
        documents: list[str],
        top_k: int | None = None,
    ) -> list[tuple[int, float]]:
        """Rerank documents by relevance to query.
        
        Args:
            query: Search query
            documents: List of document texts
            top_k: Number of results to return (None = all)
            
        Returns:
            List of (original_index, score) sorted by score descending
        """
        if not documents:
            return []

        if self.model is None:
            logger.warning("Cross-encoder not available, returning original order")
            return [(i, 1.0 - i * 0.01) for i in range(len(documents))]

        # Create query-document pairs
        pairs = [[query, doc] for doc in documents]

        # Get scores from cross-encoder
        scores = self.model.predict(pairs)

        # Sort by score
        scored = list(enumerate(scores))
        scored.sort(key=lambda x: x[1], reverse=True)

        if top_k is not None:
            scored = scored[:top_k]

        return scored

    def rerank_with_metadata(
        self,
        query: str,
        items: list[Any],
        text_key: str = "content",
        top_k: int | None = None,
    ) -> list[tuple[Any, float]]:
        """Rerank items with metadata.
        
        Args:
            query: Search query
            items: List of items (dicts or objects with text attribute)
            text_key: Key/attribute name for text content
            top_k: Number of results to return
            
        Returns:
            List of (item, score) sorted by score descending
        """
        if not items:
            return []

        # Extract text from items
        documents = []
        for item in items:
            if isinstance(item, dict):
                documents.append(item.get(text_key, str(item)))
            elif hasattr(item, text_key):
                documents.append(getattr(item, text_key))
            elif hasattr(item, "content"):
                documents.append(item.content)
            else:
                documents.append(str(item))

        # Get reranked indices and scores
        reranked = self.rerank(query, documents, top_k)

        # Return items with scores
        return [(items[idx], score) for idx, score in reranked]
