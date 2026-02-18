import json
import os
from typing import Any, Dict, List, Optional

import numpy as np
from openai import OpenAI


class AIClient:
    """Wrapper for OpenAI API calls"""

    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.embedding_cache: Dict[str, List[float]] = {}

    def get_embedding(
        self, text: str, model: str = "text-embedding-3-small"
    ) -> List[float]:
        """
        Get embedding for text with caching

        Args:
            text: Text to embed
            model: Embedding model to use

        Returns:
            List of floats (embedding vector)
        """
        # Check cache
        cache_key = f"{model}:{text[:100]}"  # Use first 100 chars as key
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]

        # Get embedding from API
        response = self.client.embeddings.create(model=model, input=text)

        embedding = response.data[0].embedding
        self.embedding_cache[cache_key] = embedding

        return embedding

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        response_format: Optional[Dict] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Get chat completion

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use
            response_format: Optional format specification (e.g., {"type": "json_object"})
            temperature: Sampling temperature

        Returns:
            Response content as string
        """
        params = {"model": model, "messages": messages, "temperature": temperature}

        if response_format:
            params["response_format"] = response_format

        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content

    def chat_completion_json(
        self, messages: List[Dict[str, str]], model: str = "gpt-4o-mini"
    ) -> Dict[str, Any]:
        """
        Get chat completion with JSON response

        Returns:
            Parsed JSON dict
        """
        content = self.chat_completion(
            messages=messages,
            model=model,
            response_format={"type": "json_object"},
            temperature=0.3,  # Lower temperature for structured output
        )

        return json.loads(content)


def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """Calculate cosine similarity between two embeddings"""
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)

    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    return dot_product / (norm1 * norm2)
