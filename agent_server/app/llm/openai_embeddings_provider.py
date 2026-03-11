from openai import OpenAI

from app.config.settings import get_settings
from app.llm.embeddings_provider import BaseEmbeddingsProvider


class OpenAiEmbeddingsProvider(BaseEmbeddingsProvider):
    def __init__(self) -> None:
        settings = get_settings()

        client_kwargs = {
            "api_key": settings.embedding_api_key,
        }
        if settings.embedding_base_url:
            client_kwargs["base_url"] = settings.embedding_base_url

        self.client = OpenAI(**client_kwargs)
        self.model = settings.embedding_model
        self.dimensions = settings.embedding_dimensions

    def embed_text(self, text: str) -> list[float]:
        kwargs = {
            "model": self.model,
            "input": text,
            "encoding_format": "float",
        }

        if self.dimensions:
            kwargs["dimensions"] = self.dimensions

        response = self.client.embeddings.create(**kwargs)
        return response.data[0].embedding

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        kwargs = {
            "model": self.model,
            "input": texts,
            "encoding_format": "float",
        }

        if self.dimensions:
            kwargs["dimensions"] = self.dimensions

        response = self.client.embeddings.create(**kwargs)
        return [item.embedding for item in response.data]