from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import logging

from fastapi import FastAPI

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("application starting...")
    # 后续在这里初始化：
    # - database connection check
    # - redis connection check
    # - llm client
    # - tool registry
    yield
    logger.info("application shutting down...")