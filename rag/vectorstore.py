"""Dependency-free lexical retrieval for local and offline RAG."""

import re


def _terms(text: str) -> set[str]:
    normalized = re.sub(r"\s+", " ", text.lower()).strip()
    words = set(re.findall(r"[\w]+", normalized))
    # Character n-grams provide useful matching for Japanese text without a tokenizer.
    compact = re.sub(r"\s+", "", normalized)
    words.update(compact[index:index + 2] for index in range(max(0, len(compact) - 1)))
    return {word for word in words if word}


class VectorStore:
    def __init__(self):
        self.documents = []
        self._document_terms: list[set[str]] = []

    def build(self, documents):
        self.documents = list(documents)
        self._document_terms = [_terms(document.page_content) for document in self.documents]

    def search(self, query, k=3):
        query_terms = _terms(query)
        scored = []
        for document, terms in zip(self.documents, self._document_terms):
            union = query_terms | terms
            score = len(query_terms & terms) / len(union) if union else 0.0
            scored.append((document, score))
        return sorted(scored, key=lambda item: item[1], reverse=True)[:k]
