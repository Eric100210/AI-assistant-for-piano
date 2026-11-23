"""Shared, lazily-created LLM client."""

from functools import lru_cache

from langchain_ollama import ChatOllama

from musaic.config import LLM_MODEL, OLLAMA_BASE_URL


@lru_cache(maxsize=1)
def get_llm() -> ChatOllama:
    """Return the shared LLM instance, created on first use."""
    return ChatOllama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL, temperature=0)
