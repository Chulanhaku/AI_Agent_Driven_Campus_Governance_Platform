from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import logging

from fastapi import FastAPI

from app.app_container import AppContainer
from app.config.settings import get_settings
from app.llm.local_embeddings_provider import LocalEmbeddingsProvider
from app.llm.local_provider import LocalLlmProvider
from app.llm.openai_embeddings_provider import OpenAiEmbeddingsProvider
from app.llm.openai_provider import OpenAiProvider
from app.rag.rag_service import RagService

logger = logging.getLogger(__name__)


def build_llm_provider():
    settings = get_settings()

    if settings.llm_provider == "openai":
        logger.info("using OpenAI provider")
        return OpenAiProvider()

    logger.info("using Local/Mock provider")
    return LocalLlmProvider()


def build_embeddings_provider():
    settings = get_settings()

    if settings.embedding_provider == "openai":
        logger.info(
            "using OpenAI embeddings provider: model=%s dimensions=%s",
            settings.embedding_model,
            settings.embedding_dimensions,
        )
        return OpenAiEmbeddingsProvider()

    logger.info("using Local embeddings provider")
    return LocalEmbeddingsProvider(dimensions=256)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("application starting...")

    llm_provider = build_llm_provider()
    embeddings_provider = build_embeddings_provider()

    rag_service = RagService(
        embeddings_provider=embeddings_provider,
    )
    try:
        rag_service.build_index()
        logger.info("rag index build success")
    except Exception as exc:
        logger.exception("rag index build failed, skip startup indexing: %s", exc)

    app.state.container = AppContainer(
        llm_provider=llm_provider,
        embeddings_provider=embeddings_provider,
        rag_service=rag_service,
    )

    logger.info("application container initialized")
    yield

    logger.info("application shutting down...")