# retriever.py を修正
class Retriever:
    def __init__(self, vectorstore, threshold=0.4):
        self.vectorstore = vectorstore
        self.threshold = threshold

    def retrieve(self, query):
        results = self.vectorstore.search(query)

        filtered = []
        for doc, score in results:
            if score >= self.threshold:
                filtered.append(doc)

        return filtered
