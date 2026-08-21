from .tool import Tool


class RagTool(Tool):
    name = "rag_search"
    description = "Searches information in locally stored documents."

    def __init__(self, retriever, sourced_memory=None):
        self.retriever = retriever
        self.sourced_memory = sourced_memory

    def execute(self, input: str) -> str:
        documents = self.retriever.retrieve(input)
        local_results = [document.page_content for document in documents]
        sourced_results = []
        if self.sourced_memory:
            sourced_results = [
                f"[Source: {item['source']}; captured: {item['captured_at']}; URL: {item.get('url', '')}]\n{item['content']}"
                for item in self.sourced_memory.search(input)
            ]
        results = local_results + sourced_results
        if not results:
            return "No relevant local documents were found."
        return "\n\n".join(results)
