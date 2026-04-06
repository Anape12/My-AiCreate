class RagPipeline:
    def __init__(self, retriever, generator):
        self.retriever = retriever
        self.generator = generator

    def run(self, query):
        # docs = self.retriever.retrieve(query)
        results = vs.search(query)
        filtered = [doc for doc, score in results if score < 0.4]
        return self.generator.generate(query, filtered)
