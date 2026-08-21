from collections.abc import Iterator

from rag.external_llm import ExternalLLMClient

from .base import LLMProvider


class ExternalProvider(LLMProvider):
    def __init__(self):
        self.client = ExternalLLMClient()
        self.model_name = self.client.model

    def invoke(self, prompt: str) -> str:
        return self.client.generate(prompt)

    def stream(self, prompt: str) -> Iterator[str]:
        yield self.invoke(prompt)

    def warmup(self) -> None:
        return None
