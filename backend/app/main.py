from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import generate, health
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title="ScriptForge API",
    description="Multi-agent AI content generation pipeline for Blue Foxes AI Content Lab.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-vercel-app.vercel.app"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(generate.router, prefix="/api", tags=["generate"])