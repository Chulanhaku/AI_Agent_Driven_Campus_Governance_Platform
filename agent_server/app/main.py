from fastapi import FastAPI

from app.lifecycle import lifespan
from app.config.settings import get_settings
from app.config.logging import setup_logging
from app.config.constants import API_PREFIX
from app.api.routers import health


setup_logging()
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(health.router, prefix=API_PREFIX)