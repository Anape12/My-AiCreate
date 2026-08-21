from collections.abc import Iterable

from .tool import Tool


class ToolRegistry:
    """Keeps the planner independent from concrete tool implementations."""

    def __init__(self, online: bool = False):
        self.online = online
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.requires_online and not self.online:
            return
        self._tools[tool.name] = tool

    def register_many(self, tools: Iterable[Tool]) -> None:
        for tool in tools:
            self.register(tool)

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return list(self._tools)

    def descriptions(self) -> str:
        return "\n".join(f"- {tool.name}: {tool.description}" for tool in self._tools.values())

    def execute(self, name: str, input: str) -> str:
        tool = self.get(name)
        if tool is None:
            return f"Tool '{name}' is not available in the current mode."
        try:
            return tool.execute(input)
        except Exception as exc:
            return f"Tool '{name}' could not be completed: {exc}"
