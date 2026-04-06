from langchain_ollama import OllamaLLM


class Generator:
    def __init__(self):
        self.llm = OllamaLLM(model="mistral")

    def generate(self, query, context_docs):
        if context_docs:
            context = "\n".join([doc.page_content for doc in context_docs])
            prompt = f"""
あなたは正確に回答するAIです。

以下の情報を優先して使用してください。
不足している場合のみ一般知識を使ってください。

不明な場合は推測せず「不明」と答えてください。

        --- 情報 ---
        {context}

        --- 質問 ---
        {query}
"""
        else:
            prompt = f"""
以下の質問に正確に答えてください。

質問: {query}
"""
        return self.llm.invoke(prompt)
