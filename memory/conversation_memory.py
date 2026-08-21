class ConversationMemory:
    """Keeps the most recent dialogue turns in process memory."""

    def __init__(self, max_messages: int = 6):
        self.max_messages = max_messages
        self._messages: list[dict[str, str]] = []

    def add(self, role: str, content: str) -> None:
        self._messages.append({"role": role, "content": content})
        self._messages[:] = self._messages[-self.max_messages:]

    def text(self) -> str:
        return "\n".join(f"{item['role']}: {item['content']}" for item in self._messages)
