from fastapi import FastAPI
import app.core.logging
from app.api.routes.health import router as health_router

app = FastAPI(
    title="Closira AI Assignment",
    version="1.0.0"
)

app.include_router(health_router)