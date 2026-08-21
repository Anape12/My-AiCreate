from abc import ABC, abstractmethod


class Tool(ABC):
    """A self-contained capability available to the AI planner."""

    name: str
    description: str
    requires_online: bool = False

    @abstractmethod
    def execute(self, input: str) -> str:
        """Run the tool and return text suitable for an LLM context."""
