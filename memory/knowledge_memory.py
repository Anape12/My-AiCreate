class KnowledgeMemory:
    """Adapter exposing the local knowledge base as a memory source."""

    def __init__(self, retriever):
        self.retriever = retriever

    def search(self, query: str) -> str:
        documents = self.retriever.retrieve(query)
        return "\n\n".join(document.page_content for document in documents)
