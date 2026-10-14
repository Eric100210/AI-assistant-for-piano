"""Shared, lazily-created embedding model."""

from functools import lru_cache

from langchain_ollama import OllamaEmbeddings

from musaic.config import EMBEDDING_MODEL, OLLAMA_BASE_URL


@lru_cache(maxsize=1)
def get_embedding_model():
    """Return the shared embedding model, created on first use."""
    return OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)
