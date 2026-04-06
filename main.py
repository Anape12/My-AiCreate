from rag.vectorstore import VectorStore
from rag.retriever import Retriever
from rag.generator import Generator
from rag.pipeline import RagPipeline
from langchain_text_splitters import CharacterTextSplitter

# データ
docs = ["if文は条件分岐する構文"]

# 分割
splitter = CharacterTextSplitter(chunk_size=300)
documents = splitter.create_documents(docs)

# 構築
vs = VectorStore()
vs.build(documents)

retriever = Retriever(vs, threshold=0.5)
generator = Generator()

pipeline = RagPipeline(retriever, generator)

# 実行
query = "if文とは？"
print(pipeline.run(query))

# from langchain_community.vectorstores import Chroma
# from langchain_text_splitters import CharacterTextSplitter
# from langchain_ollama import OllamaEmbeddings, OllamaLLM

# # ===== データ =====
# docs = [
#      "if文は『条件Aなら処理X』という特殊構文である（テスト用定義）"
# ]

# chunk_size=300

# k=3

# # ===== 分割 =====
# splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
# texts = splitter.create_documents(docs)

# # ===== ベクトル化 =====
# embeddings = OllamaEmbeddings(model="mistral")

# # ===== DB =====
# db = Chroma.from_documents(texts, embeddings)

# # ===== クエリ =====
# query = "if文とは？"
# results = db.similarity_search(query, k=2)

# # ===== LLM =====
# llm = OllamaLLM(model="mistral")

# context = "\n".join([doc.page_content for doc in results])

# prompt = f"""
# あなたはJavaコード解析AIです。

# 以下の情報を使って、
# 処理の実行順序をステップ形式で説明してください。

# - 変数の初期化
# - 条件分岐
# - メソッド呼び出し

# を必ず含めてください。

# {context}

# 質問: {query}
# """

# print(llm.invoke(prompt))