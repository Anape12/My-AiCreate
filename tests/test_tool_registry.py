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


class RagTool(EchoTool):
    name = "rag_search"


class WebTool(EchoTool):
    name = "web_search"
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

    def test_simple_request_uses_fast_routing_without_planner_llm(self):
        class FailingLlm:
            def invoke(self, prompt):
                raise AssertionError("planner LLM must not run for a simple request")

        registry = ToolRegistry()
        registry.register(RagTool())
        result = Planner(FailingLlm(), registry).run("Pythonについて教えて")

        self.assertEqual(result, "[rag_search]\nPythonについて教えて")

    def test_health_question_uses_web_evidence_when_online(self):
        class FailingLlm:
            def invoke(self, prompt):
                raise AssertionError("simple health routing must not need planner LLM")

        registry = ToolRegistry(online=True)
        registry.register_many([RagTool(), WebTool()])
        result = Planner(FailingLlm(), registry).run("明け方に目が覚めて眠れません")

        self.assertIn("[rag_search]", result)
        self.assertIn("[web_search]", result)


if __name__ == "__main__":
    unittest.main()
