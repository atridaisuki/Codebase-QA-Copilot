from fastapi import FastAPI

from app.config import get_settings
from app.core.error_handlers import register_exception_handlers
from app.core.logging import configure_logging, request_logging_middleware
from app.routers.health import router as health_router
from app.routers.ingest import router as ingest_router
from app.routers.agent import router as agent_router
from app.routers.qa import router as qa_router

settings = get_settings()
configure_logging()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Minimal document QA service using FastAPI, Chroma, embeddings, and Claude.",
)

app.middleware("http")(request_logging_middleware)
register_exception_handlers(app)

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(ingest_router, prefix=settings.api_prefix)
app.include_router(qa_router, prefix=settings.api_prefix)
app.include_router(agent_router, prefix=settings.api_prefix)
