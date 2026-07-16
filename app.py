from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse

from langchain_ollama import OllamaLLM
from langchain_text_splitters import CharacterTextSplitter

from rag.vectorstore import VectorStore
from rag.retriever import Retriever
from rag.quick_answers import get_quick_answer
from rag.external_llm import ExternalLLMClient
from rag.prompt_builder import build_prompt
from rag.query_guard import normalize_query
from rag.knowledge_loader import KnowledgeLoader
from rag.answer_guard import refine_answer
from rag.calculator import calculate

from tools.tools import TOOLS
from agent.react_agent import ReactAgent

# ===== 初期化 =====
app = FastAPI()

llm = OllamaLLM(model="mistral")
agent = ReactAgent(llm, TOOLS)
external_llm = ExternalLLMClient()

# 初期化コストの高い処理は起動時に1回だけ行う
# ここでは必要に応じて後で差し替え可能にしておく

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# ===== RAG =====
knowledge_loader = KnowledgeLoader("data/knowledge.txt")
raw_knowledge = knowledge_loader.load()

splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=50)
documents = splitter.create_documents(raw_knowledge)

vs = VectorStore()
vs.build(documents)

retriever = Retriever(vs, threshold=0.4)

# ===== 履歴 =====
chat_history = []
MAX_HISTORY = 6

# ===== リクエスト =====


class ChatRequest(BaseModel):
    query: str


# ===== API =====
@app.post("/chat-stream")
def chat_stream(req: ChatRequest):

    def generate():
        global chat_history

        # 履歴
        chat_history.append({"role": "user", "content": req.query})
        chat_history[:] = chat_history[-MAX_HISTORY:]

        history_text = "\n".join(
            [f"{h['role']}: {h['content']}" for h in chat_history]
        )

        quick_answer = get_quick_answer(req.query)
        if quick_answer is not None:
            yield quick_answer
            chat_history.append({"role": "assistant", "content": quick_answer})
            return

        calc_result = calculate(req.query)
        if calc_result is not None:
            answer = f"{calc_result}円です。"
            yield answer
            chat_history.append({"role": "assistant", "content": answer})
            return

        # ===== ReAct =====
        # 追加のLLMラウンドトリップを避け、1回の生成に集約する
        react_context = ""

        # ===== RAG =====
        docs = retriever.retrieve(req.query)

        rag_context = ""
        if docs:
            rag_context = "\n".join([doc.page_content for doc in docs])

        normalized_query = normalize_query(req.query)

        # ===== 最終プロンプト =====
        prompt = build_prompt(
            query=normalized_query,
            history_text=history_text,
            react_context=react_context,
            rag_context=rag_context,
        )

        full = ""

        try:
            if external_llm.api_key:
                full = external_llm.generate(prompt)
                full = refine_answer(full, rag_context)
                yield full
            else:
                for chunk in llm.stream(prompt):
                    full += chunk
                    yield chunk
                full = refine_answer(full, rag_context)
        except Exception:
            for chunk in llm.stream(prompt):
                full += chunk
                yield chunk
            full = refine_answer(full, rag_context)

        chat_history.append({"role": "assistant", "content": full})

    return StreamingResponse(generate(), media_type="text/plain")
