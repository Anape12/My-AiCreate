from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse

from langchain_ollama import OllamaLLM
from langchain_text_splitters import CharacterTextSplitter

from rag.vectorstore import VectorStore
from rag.retriever import Retriever

from tools.tools import TOOLS
from agent.react_agent import ReactAgent

# ===== 初期化 =====
app = FastAPI()

llm = OllamaLLM(model="mistral")
agent = ReactAgent(llm, TOOLS)

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
docs = ["if文は条件分岐する構文"]

splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=50)
documents = splitter.create_documents(docs)

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

        # ===== ReAct =====
        react_context = agent.run(req.query)

        # ===== RAG =====
        docs = retriever.retrieve(req.query)

        rag_context = ""
        if docs:
            rag_context = "\n".join([doc.page_content for doc in docs])

        # ===== 最終プロンプト =====
        prompt = f"""
あなたは優秀なAIアシスタントです。

# ルール
- ツール結果を優先
- 推測禁止
- 分からない場合は「分かりません」

# 会話履歴
{history_text}

# エージェント情報
{react_context}

# 参考情報
{rag_context}

# 質問
{req.query}
"""

        full = ""

        for chunk in llm.stream(prompt):
            full += chunk
            yield chunk

        chat_history.append({"role": "assistant", "content": full})

    return StreamingResponse(generate(), media_type="text/plain")
