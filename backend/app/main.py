import os
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import generate, health
from app.core.logging import setup_logging

# --------------------------------------------------
# 1. Configure application logging
# --------------------------------------------------

setup_logging()


# --------------------------------------------------
# 2. Initialize FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="ScriptForge API",
    description=(
        "Multi-agent AI content generation pipeline for Blue Foxes AI Content Lab."
    ),
    version="1.0.0",
)


# --------------------------------------------------
# 3. Configure allowed frontend origins
# --------------------------------------------------


def get_allowed_origins() -> list[str]:
    """
    Allow local development and the production
    frontend configured in Railway.
    """

    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    frontend_url = os.getenv("FRONTEND_URL", "").strip().rstrip("/")

    if frontend_url:
        parsed = urlparse(frontend_url)

        if (
            parsed.scheme not in ("http", "https")
            or not parsed.netloc
            or parsed.username
            or parsed.password
            or parsed.path not in ("", "/")
            or parsed.params
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError(
                "FRONTEND_URL must be a valid frontend origin, "
                "such as https://scriptforge.vercel.app"
            )

        origins.append(frontend_url)

    return origins


# --------------------------------------------------
# 4. Configure CORS middleware
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# --------------------------------------------------
# 5. Register API routes
# --------------------------------------------------

app.include_router(
    health.router,
    prefix="/api",
    tags=["health"],
)

app.include_router(
    generate.router,
    prefix="/api",
    tags=["generate"],
)
