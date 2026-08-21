import unittest

from agent.planner import Planner
from tools.registry import ToolRegistry
from tools.tool import Tool


class EchoTool(Tool):
    name = "echo"
    description = "Returns its input."

    def execute(self, input: str) -> str:
        return input


class OnlineTool(EchoTool):
    name = "online"
    requires_online = True


class ToolRegistryTests(unittest.TestCase):
    def test_offline_registry_excludes_online_tools(self):
        registry = ToolRegistry(online=False)
        registry.register_many([EchoTool(), OnlineTool()])

        self.assertEqual(registry.names(), ["echo"])

    def test_planner_executes_available_tool_once(self):
        class Llm:
            def invoke(self, prompt):
                return '{"actions": ["echo"]}'

        registry = ToolRegistry()
        registry.register(EchoTool())
        result = Planner(Llm(), registry).run("hello")

        self.assertEqual(result, "[echo]\nhello")


if __name__ == "__main__":
    unittest.main()
