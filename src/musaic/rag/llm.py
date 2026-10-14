"""Shared, lazily-created LLM client."""

from functools import lru_cache

from langchain_ollama import OllamaLLM

from musaic.config import LLM_MODEL, OLLAMA_BASE_URL


@lru_cache(maxsize=1)
def get_llm():
    """Return the shared LLM instance, created on first use."""
    return OllamaLLM(model=LLM_MODEL, base_url=OLLAMA_BASE_URL)
