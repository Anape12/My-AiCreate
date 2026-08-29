import os
from pathlib import Path

from langchain_text_splitters import CharacterTextSplitter

from agent.planner import Planner
from learning import EvaluationGate
from memory import ConversationMemory, ExperienceMemory, KnowledgeMemory
from memory.sourced_knowledge_memory import SourcedKnowledgeMemory
from rag.answer_guard import refine_answer
from rag.knowledge_loader import KnowledgeLoader
from rag.prompt_builder import build_prompt
from rag.query_guard import normalize_query
from rag.quick_answers import get_quick_answer
from rag.retriever import Retriever
from rag.vectorstore import VectorStore
from tools.calculator_tool import CalculatorTool
from tools.rag_tool import RagTool
from tools.registry import ToolRegistry
from tools.train_tool import TrainTool
from tools.training_export_tool import TrainingExportTool
from tools.weather_tool import WeatherTool
from tools.web_search_tool import WebSearchTool
from training.model_registry import ModelRegistry
from providers import create_llm_provider


class AIService:
    """Application service coordinating memory, planning, tools, and model output."""

    def __init__(self, online: bool | None = None):
        self.online = online if online is not None else os.getenv("AI_ONLINE", "false").lower() == "true"
        project_root = Path(__file__).resolve().parent
        self.conversation_memory = ConversationMemory(max_messages=6)
        self.experience_memory = ExperienceMemory(project_root / "data" / "experiences.jsonl")
        self.sourced_knowledge_memory = SourcedKnowledgeMemory(project_root / "data" / "sourced_knowledge.jsonl")
        self.model_registry = ModelRegistry(project_root / "data" / "models.json")
        self.model_name = self.model_registry.active_runtime_model() or os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
        self.llm = create_llm_provider(self.model_name)
        self.evaluation_gate = EvaluationGate()
        self.registry, self.knowledge_memory = self._build_registry()
        self.planner = Planner(self.llm, self.registry)

    def _build_registry(self) -> tuple[ToolRegistry, KnowledgeMemory]:
        project_root = Path(__file__).resolve().parent
        loader = KnowledgeLoader(str(project_root / "data" / "knowledge.txt"))
        splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=50)
        documents = splitter.create_documents(loader.load())
        vectorstore = VectorStore()
        vectorstore.build(documents)
        retriever = Retriever(vectorstore, threshold=0.08)
        knowledge_memory = KnowledgeMemory(retriever)
        registry = ToolRegistry(online=self.online)
        registry.register_many([
            RagTool(retriever, self.sourced_knowledge_memory), CalculatorTool(), WeatherTool(),
            TrainTool(),
            TrainingExportTool(
                self.experience_memory,
                project_root / "data" / "training" / "experiences.jsonl",
                self.model_name,
            ),
            WebSearchTool(self.sourced_knowledge_memory)
        ])
        return registry, knowledge_memory

    def _history_text(self) -> str:
        return self.conversation_memory.text()

    def warmup(self) -> None:
        self.llm.warmup()

    def _model_error(self, error: Exception) -> str:
        return (
            f"LLM provider could not use model '{self.model_name}'. "
            "Check LLM_PROVIDER and the configured model, then restart the API. "
            f"Details: {error}"
        )

    def stream(self, query: str, experience_id: str | None = None):
        self.conversation_memory.add("user", query)
        quick_answer = get_quick_answer(query)
        if quick_answer is not None:
            self.conversation_memory.add("assistant", quick_answer)
            evaluation_passed, evaluation_note = self.evaluation_gate.evaluate(quick_answer, "", True)
            self.experience_memory.save({
                **({"id": experience_id} if experience_id else {}),
                "query": query,
                "plan": [],
                "tool_results": "",
                "answer": quick_answer,
                "success": evaluation_passed,
                "evaluation_note": evaluation_note,
            })
            yield quick_answer
            return

        experience_context = "\n".join(
            f"Past query: {item['query']}\nPast plan: {', '.join(item.get('plan', []))}"
            for item in self.experience_memory.search(query)
        )
        plan = self.planner.run_with_trace(query, experience_context=experience_context)
        tool_context = plan.context
        prompt = build_prompt(normalize_query(query), self._history_text(), tool_context, "")
        full = ""
        try:
            for chunk in self.llm.stream(prompt):
                full += chunk
                yield chunk
        except Exception as error:
            full = self._model_error(error)
            yield full
        full = refine_answer(full, tool_context)
        self.conversation_memory.add("assistant", full)
        evaluation_passed, evaluation_note = self.evaluation_gate.evaluate(
            full, tool_context, not full.startswith("LLM provider could not")
        )
        self.experience_memory.save({
            **({"id": experience_id} if experience_id else {}),
            "query": query,
            "plan": plan.actions,
            "tool_results": tool_context,
            "answer": full,
            "success": evaluation_passed,
            "evaluation_note": evaluation_note,
        })
