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
from app.self_iteration.capability_registry import CapabilityRegistry
from sqlalchemy.orm import Session

from app.db.repositories.capability_proposal_repository import CapabilityProposalRepository
from app.self_iteration.capability_bootstrap import CapabilityBootstrap
from app.self_iteration.capability_loader import CapabilityLoader

from app.self_iteration.dynamic_tool_registry import DynamicToolRegistry
from app.self_iteration.dynamic_plan_registry import DynamicPlanRegistry
from app.self_iteration.dynamic_capability_bootstrap import DynamicCapabilityBootstrap
from app.db.repositories.dynamic_tool_definition_repository import DynamicToolDefinitionRepository
from app.db.repositories.dynamic_plan_definition_repository import DynamicPlanDefinitionRepository

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
    capability_registry = CapabilityRegistry()
    dynamic_tool_registry = DynamicToolRegistry()
    dynamic_plan_registry = DynamicPlanRegistry()
    bootstrap_result = None
    db: Session | None = None
    try:
        db = SessionLocal()
        capability_proposal_repository = CapabilityProposalRepository(db)
        capability_loader = CapabilityLoader(capability_registry)
        capability_bootstrap = CapabilityBootstrap(
            capability_proposal_repository=capability_proposal_repository,
            capability_loader=capability_loader,
        )
        bootstrap_result = capability_bootstrap.reload_activated_proposals()
        logger.info("capability bootstrap result: %s", bootstrap_result)

        dynamic_tool_definition_repository = DynamicToolDefinitionRepository(db)
        dynamic_plan_definition_repository = DynamicPlanDefinitionRepository(db)
        dynamic_bootstrap = DynamicCapabilityBootstrap(
            dynamic_tool_definition_repository=dynamic_tool_definition_repository,
            dynamic_plan_definition_repository=dynamic_plan_definition_repository,
            dynamic_tool_registry=dynamic_tool_registry,
            dynamic_plan_registry=dynamic_plan_registry,
        )
        dynamic_bootstrap_result = dynamic_bootstrap.reload_active_definitions()
        logger.info("dynamic capability bootstrap result: %s", dynamic_bootstrap_result)


    except Exception as exc:
        logger.exception("capability bootstrap failed: %s", exc)
    finally:
        if db is not None:
            db.close()



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
        capability_registry=capability_registry,
        dynamic_tool_registry=dynamic_tool_registry,
        dynamic_plan_registry=dynamic_plan_registry,
    )

    logger.info("application container initialized")
    yield

    logger.info("application shutting down...")
