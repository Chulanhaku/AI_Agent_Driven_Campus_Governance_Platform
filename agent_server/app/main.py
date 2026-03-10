from fastapi import FastAPI

from app.lifecycle import lifespan
from app.config.settings import get_settings
from app.config.logging import setup_logging
from app.config.constants import API_PREFIX
from app.api.routers import audit, campus_card, health, leave, schedule,auth,chat


setup_logging()
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(health.router, prefix=API_PREFIX)
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(schedule.router, prefix=API_PREFIX)
app.include_router(chat.router, prefix=API_PREFIX)
app.include_router(campus_card.router, prefix=API_PREFIX)
app.include_router(leave.router, prefix=API_PREFIX)
app.include_router(audit.router, prefix=API_PREFIX)