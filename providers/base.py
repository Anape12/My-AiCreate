from abc import ABC, abstractmethod
from collections.abc import Iterator


class LLMProvider(ABC):
    """Provider-neutral interface for planning and answer generation."""

    model_name: str

    @abstractmethod
    def invoke(self, prompt: str) -> str:
        pass

    @abstractmethod
    def stream(self, prompt: str) -> Iterator[str]:
        pass

    def warmup(self) -> None:
        """Optionally load the model before the first user request."""
