import math


class InMemoryVectorStore:
    def __init__(self, embeddings_provider) -> None:
        self.embeddings_provider = embeddings_provider
        self.items: list[dict] = []

    def add_texts(self, texts: list[dict]) -> None:
        contents = [item["content"] for item in texts]
        embeddings = self.embeddings_provider.embed_texts(contents)

        for item, embedding in zip(texts, embeddings, strict=False):
            self.items.append(
                {
                    **item,
                    "embedding": embedding,
                }
            )

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        query_embedding = self.embeddings_provider.embed_text(query)

        scored_items = []
        for item in self.items:
            score = self._cosine_similarity(query_embedding, item["embedding"])
            scored_items.append(
                {
                    **item,
                    "score": score,
                }
            )

        scored_items.sort(key=lambda x: x["score"], reverse=True)
        return scored_items[:top_k]

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b, strict=False))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)