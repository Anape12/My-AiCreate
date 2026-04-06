from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings


class VectorStore:
    def __init__(self):
        self.embedding = OllamaEmbeddings(model="nomic-embed-text")
        self.db = None

    def build(self, documents):
        self.db = Chroma.from_documents(documents, self.embedding)

    def search(self, query, k=3):
        return self.db.similarity_search_with_score(query, k=k)
