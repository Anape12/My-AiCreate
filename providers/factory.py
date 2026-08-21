import os

from .base import LLMProvider
from .external_provider import ExternalProvider
from .ollama_provider import OllamaProvider


def create_llm_provider(model_name: str) -> LLMProvider:
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider == "external":
        return ExternalProvider()
    if provider == "ollama":
        return OllamaProvider(model_name)
    raise ValueError("LLM_PROVIDER must be 'ollama' or 'external'.")
