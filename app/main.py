from fastapi import FastAPI
from app.routers.health import router as health_router
from app.routers.documents import router as documents_router
from app.routers.stats import router as stats_router

app = FastAPI(
    title="Smart Web Data Pipeline",
    version="1.0.0",
    description="Safe web extraction, normalization, deduplication, PostgreSQL storage and optional LLM analysis.",
)
app.include_router(health_router)
app.include_router(documents_router)
app.include_router(stats_router)
