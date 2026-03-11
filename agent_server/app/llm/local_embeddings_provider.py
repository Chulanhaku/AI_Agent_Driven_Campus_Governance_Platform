import hashlib
import math

from app.llm.embeddings_provider import BaseEmbeddingsProvider


class LocalEmbeddingsProvider(BaseEmbeddingsProvider):
    def __init__(self, dimensions: int = 256) -> None:
        self.dimensions = dimensions

    def embed_text(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions

        text = text.strip().lower()
        if not text:
            return vector

        for token in self._tokenize(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            for i in range(0, min(len(digest), self.dimensions)):
                vector[i] += (digest[i] / 255.0) - 0.5

        return self._normalize(vector)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(text) for text in texts]

    def _tokenize(self, text: str) -> list[str]:
        english_tokens = []
        current = []

        for ch in text:
            if ch.isalnum() or ch == "_":
                current.append(ch)
            else:
                if current:
                    english_tokens.append("".join(current))
                    current = []

        if current:
            english_tokens.append("".join(current))

        chinese_chars = [ch for ch in text if "\u4e00" <= ch <= "\u9fff"]

        return english_tokens + chinese_chars

    def _normalize(self, vector: list[float]) -> list[float]:
        norm = math.sqrt(sum(v * v for v in vector))
        if norm == 0:
            return vector
        return [v / norm for v in vector]