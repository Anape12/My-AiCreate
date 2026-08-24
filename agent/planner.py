import json
from dataclasses import dataclass

from tools.registry import ToolRegistry


@dataclass
class PlanResult:
    context: str
    actions: list[str]


class Planner:
    """Chooses available tools, executes them, and returns their evidence."""

    def __init__(self, llm, registry: ToolRegistry):
        self.llm = llm
        self.registry = registry

    def _prompt(self, query: str, context: str) -> str:
        return f"""You are an AI planner. Select zero or more tools required to answer the user.
Return JSON only: {{\"actions\": [\"tool_name\"]}}.
Only use names from the available tools list.

Available tools:
{self.registry.descriptions()}

Question: {query}
Previous tool results: {context}
"""

    def _parse_actions(self, response: str) -> list[str]:
        try:
            data = json.loads(response.replace("```json", "").replace("```", "").strip())
            actions = data.get("actions", [])
            return [action for action in actions if action in self.registry.names()]
        except (json.JSONDecodeError, AttributeError):
            return []

    def _fallback_actions(self, query: str) -> list[str]:
        actions = []
        if "rag_search" in self.registry.names():
            actions.append("rag_search")
        if any(char.isdigit() for char in query) and "calculator" in self.registry.names():
            actions.append("calculator")
        if any(word in query.lower() for word in ("天気", "weather", "雨", "傘")) and "weather" in self.registry.names():
            actions.append("weather")
        if any(word in query.lower() for word in ("電車", "列車", "運行", "train")) and "train" in self.registry.names():
            actions.append("train")
        if any(word in query.lower() for word in ("学習データ", "fine-tuning", "ファインチューニング")) and "export_training_data" in self.registry.names():
            actions.append("export_training_data")
        if any(word in query.lower() for word in ("検索", "調べて", "search")) and "web_search" in self.registry.names():
            actions.append("web_search")
        high_stakes_terms = (
            "眠", "睡眠", "不眠", "体調", "症状", "痛み", "薬", "病気",
            "診断", "法律", "契約", "税金", "投資", "ローン",
        )
        if any(word in query for word in high_stakes_terms) and "web_search" in self.registry.names():
            actions.append("web_search")
        return list(dict.fromkeys(actions))

    def run(self, query: str, max_steps: int = 3) -> str:
        return self.run_with_trace(query, max_steps).context

    def run_with_trace(self, query: str, max_steps: int = 3, experience_context: str = "") -> PlanResult:
        """Use deterministic routing first; reserve LLM planning for complex requests."""
        context = ""
        executed: set[str] = set()
        action_trace: list[str] = []

        def execute(actions: list[str]) -> None:
            nonlocal context
            actions = [action for action in actions if action not in executed]
            if not actions:
                return
            results = [f"[{name}]\n{self.registry.execute(name, query)}" for name in actions]
            executed.update(actions)
            action_trace.extend(actions)
            context = "\n\n".join([context, *results]).strip()

        fast_actions = self._fallback_actions(query)
        if fast_actions:
            execute(fast_actions)
            # Weather + transit + web requests benefit from one additional planning pass.
            online_actions = {"weather", "train", "web_search"} & set(fast_actions)
            if len(online_actions) < 2:
                return PlanResult(context=context, actions=action_trace)

        # An LLM plan is only needed for a multi-source request or an unknown custom tool.
        for _ in range(1 if fast_actions else min(max_steps, 1)):
            try:
                actions = self._parse_actions(self.llm.invoke(self._prompt(query, experience_context + "\n" + context)))
            except Exception:
                actions = []
            if not actions and not context:
                actions = fast_actions
            if not actions:
                break
            execute(actions)
        return PlanResult(context=context, actions=action_trace)
