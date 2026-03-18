from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import logging

from fastapi import FastAPI
from sqlalchemy import text

from app.app_container import AppContainer
from app.config.settings import get_settings
from app.db.session import SessionLocal
from app.llm.local_embeddings_provider import LocalEmbeddingsProvider
from app.llm.local_provider import LocalLlmProvider
from app.llm.openai_embeddings_provider import OpenAiEmbeddingsProvider
from app.llm.openai_provider import OpenAiProvider
from app.rag.rag_service import RagService
from database.seeds.seed_policy_handbook import seed_policy_handbook

logger = logging.getLogger(__name__)


def try_seed_policy_handbook_on_startup() -> None:
    settings = get_settings()
    if not settings.policy_handbook_auto_seed_on_startup:
        return

    try:
        with SessionLocal() as db:
            count = db.execute(
                text("SELECT COUNT(*) FROM policy_handbook_nodes")
            ).scalar_one()
    except Exception as exc:
        logger.info("skip policy handbook auto seed: %s", exc)
        return

    if int(count or 0) > 0:
        logger.info("skip policy handbook auto seed: existing rows=%s", count)
        return

    try:
        seed_policy_handbook(
            jsonl_path=settings.policy_handbook_jsonl_path,
            sqlite_path="",
            replace=False,
        )
        logger.info("policy handbook auto seed success")
    except Exception as exc:
        logger.exception("policy handbook auto seed failed: %s", exc)


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

    try_seed_policy_handbook_on_startup()

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