
import os
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, generate, health
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
        "Multi-agent AI content generation pipeline "
        "for Blue Foxes AI Content Lab."
    ),
    version="1.0.0",
)


# --------------------------------------------------
# 3. Configure allowed frontend origins
# --------------------------------------------------

def get_allowed_origins() -> list[str]:
    """
    Allow local React development and explicitly
    configured production frontend origins.

    FRONTEND_URL may contain one or more
    comma-separated origins.
    """

    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    frontend_urls = os.getenv(
        "FRONTEND_URL", ""
    ).strip()

    if frontend_urls:
        for frontend_url in frontend_urls.split(","):
            frontend_url = frontend_url.strip().rstrip("/")

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
                    "FRONTEND_URL must contain valid origins, "
                    "such as https://scriptforge.vercel.app"
                )

            origins.append(frontend_url)

    return list(dict.fromkeys(origins))


# --------------------------------------------------
# 4. Configure CORS middleware
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "OPTIONS",
    ],
    allow_headers=[
        "Content-Type",
        "X-CSRF-Token",
    ],
)


# --------------------------------------------------
# 5. Register health routes
# --------------------------------------------------

app.include_router(
    health.router,
    prefix="/api",
    tags=["health"],
)


# --------------------------------------------------
# 6. Register AI generation and approval routes
# --------------------------------------------------

app.include_router(
    generate.router,
    prefix="/api",
    tags=["generate"],
)


# --------------------------------------------------
# 7. Register administrator authentication routes
# --------------------------------------------------

app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["authentication"],
)
