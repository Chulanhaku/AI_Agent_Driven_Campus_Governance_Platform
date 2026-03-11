from app.rag.vector_store import InMemoryVectorStore


class Retriever:
    def __init__(self, vector_store: InMemoryVectorStore) -> None:
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        return self.vector_store.search(query=query, top_k=top_k)