from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.lifecycle import lifespan
from app.config.settings import get_settings
from app.config.logging import setup_logging
from app.config.constants import API_PREFIX
from app.api.routers import admin, audit, auth, campus_card, chat, health, leave, schedule, resource_booking, notification, approval, capability


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
app.include_router(admin.router, prefix=API_PREFIX)
app.include_router(resource_booking.router, prefix=API_PREFIX)
app.include_router(notification.router, prefix=API_PREFIX)
app.include_router(approval.router, prefix=API_PREFIX)
app.include_router(capability.router, prefix=API_PREFIX)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)