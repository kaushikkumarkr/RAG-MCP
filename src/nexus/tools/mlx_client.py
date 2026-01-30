"""MLX-LM integration for local LLM testing."""

import json
from typing import Any

import httpx
from loguru import logger


class MLXLMClient:
    """Client for MLX-LM server (OpenAI-compatible API)."""

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        model: str = "mlx-community/Qwen2.5-7B-Instruct-4bit",
        timeout: float = 120.0,
    ) -> None:
        """Initialize MLX-LM client.
        
        Args:
            base_url: MLX-LM server URL
            model: Model name for API calls
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Send chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response text
        """
        try:
            response = self._client.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except httpx.ConnectError:
            logger.error(f"Cannot connect to MLX-LM at {self.base_url}")
            raise ConnectionError(
                f"MLX-LM server not running at {self.base_url}. "
                f"Start it with: mlx_lm.server --model {self.model} --port 8080"
            )
        except Exception as e:
            logger.error(f"MLX-LM request failed: {e}")
            raise

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Generate text from a prompt.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature=temperature, max_tokens=max_tokens)

    def is_available(self) -> bool:
        """Check if MLX-LM server is available."""
        try:
            response = self._client.get(f"{self.base_url}/v1/models")
            return response.status_code == 200
        except Exception:
            return False

    def close(self) -> None:
        """Close the client."""
        self._client.close()


class NexusMCPTester:
    """Test Nexus MCP tools using MLX-LM."""

    def __init__(
        self,
        llm_client: MLXLMClient,
        search_func: Any,
    ) -> None:
        """Initialize tester.
        
        Args:
            llm_client: MLX-LM client
            search_func: Function to call for search (returns SearchResult list)
        """
        self.llm = llm_client
        self.search = search_func

    def answer_question(
        self,
        question: str,
        top_k: int = 3,
    ) -> dict[str, Any]:
        """Answer a question using RAG.
        
        Args:
            question: User question
            top_k: Number of context chunks to retrieve
            
        Returns:
            Dict with question, contexts, and answer
        """
        # Retrieve contexts
        results = self.search(query=question, top_k=top_k)
        contexts = [r.content for r in results]
        
        # Build prompt
        context_text = "\n\n---\n\n".join(contexts)
        prompt = f"""Use the following context to answer the question. If the answer is not in the context, say "I don't have enough information."

Context:
{context_text}

Question: {question}

Answer:"""

        # Generate answer
        answer = self.llm.generate(prompt, temperature=0.3, max_tokens=512)
        
        return {
            "question": question,
            "contexts": contexts,
            "answer": answer,
            "sources": [r.source for r in results],
        }

    def run_test_questions(
        self,
        questions: list[str],
    ) -> list[dict[str, Any]]:
        """Run a batch of test questions.
        
        Args:
            questions: List of questions to test
            
        Returns:
            List of answer results
        """
        results = []
        for q in questions:
            logger.info(f"Testing: {q}")
            try:
                result = self.answer_question(q)
                results.append(result)
            except Exception as e:
                logger.error(f"Error on question '{q}': {e}")
                results.append({
                    "question": q,
                    "error": str(e),
                })
        return results
