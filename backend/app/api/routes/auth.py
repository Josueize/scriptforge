
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    Header,
    HTTPException,
    Request,
    Response,
    status,
)
from pydantic import BaseModel, Field
from pwdlib import PasswordHash

from app.core.config import settings


router = APIRouter()
password_hash = PasswordHash.recommended()

SESSION_COOKIE = "scriptforge_session"
ALGORITHM = "HS256"
ISSUER = "scriptforge"
AUDIENCE = "scriptforge-admin"


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class AuthResponse(BaseModel):
    authenticated: bool
    username: str


class SessionResponse(AuthResponse):
    csrf_token: str


def validate_auth_config() -> None:
    if (
        not settings.admin_username
        or not settings.admin_password_hash
        or len(settings.session_secret_key) < 32
        or settings.session_expire_minutes <= 0
    ):
        raise HTTPException(
            status_code=503,
            detail="Administrator authentication is not configured.",
        )


def cookie_options(request: Request) -> dict:
    """
    Local development uses SameSite=Lax.

    Production cookie settings are controlled by
    explicit environment configuration, not by
    trusting arbitrary forwarded request headers.
    """
    import os

    production = os.getenv(
        "AUTH_COOKIE_SECURE", "false"
    ).lower() == "true"

    return {
        "httponly": True,
        "secure": production,
        "samesite": "none" if production else "lax",
        "path": "/",
    }


def create_session_token(username: str, csrf_token: str) -> str:
    now = datetime.now(timezone.utc)

    expires = now + timedelta(
        minutes=settings.session_expire_minutes
    )

    payload = {
        "sub": username,
        "csrf": csrf_token,
        "iat": now,
        "exp": expires,
        "iss": ISSUER,
        "aud": AUDIENCE,
    }

    return jwt.encode(
        payload,
        settings.session_secret_key,
        algorithm=ALGORITHM,
    )


def require_admin(
    session_token: str | None = Cookie(
        default=None,
        alias=SESSION_COOKIE,
    ),
) -> dict:
    validate_auth_config()

    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    try:
        payload = jwt.decode(
            session_token,
            settings.session_secret_key,
            algorithms=[ALGORITHM],
            issuer=ISSUER,
            audience=AUDIENCE,
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session.",
        ) from exc

    username = payload.get("sub")
    csrf_token = payload.get("csrf")

    if not isinstance(username, str):
        raise HTTPException(
            status_code=401,
            detail="Invalid session.",
        )

    if not isinstance(csrf_token, str) or not csrf_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid session.",
        )

    if not secrets.compare_digest(
        username,
        settings.admin_username,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required.",
        )

    return payload


def require_csrf(
    session: dict = Depends(require_admin),
    csrf_header: str | None = Header(
        default=None,
        alias="X-CSRF-Token",
    ),
) -> dict:
    expected = session["csrf"]

    if (
        not csrf_header
        or not secrets.compare_digest(csrf_header, expected)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed.",
        )

    return session


@router.post("/login", response_model=SessionResponse)
async def login(
    credentials: LoginRequest,
    request: Request,
    response: Response,
) -> SessionResponse:
    validate_auth_config()

    username_valid = secrets.compare_digest(
        credentials.username,
        settings.admin_username,
    )

    try:
        password_valid = password_hash.verify(
            credentials.password,
            settings.admin_password_hash,
        )
    except (ValueError, TypeError):
        password_valid = False

    if not username_valid or not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    csrf_token = secrets.token_urlsafe(32)

    session_token = create_session_token(
        settings.admin_username,
        csrf_token,
    )

    response.set_cookie(
        key=SESSION_COOKIE,
        value=session_token,
        max_age=settings.session_expire_minutes * 60,
        **cookie_options(request),
    )

    response.headers["Cache-Control"] = "no-store"

    return SessionResponse(
        authenticated=True,
        username=settings.admin_username,
        csrf_token=csrf_token,
    )


@router.get("/me", response_model=SessionResponse)
async def get_current_admin(
    response: Response,
    session: dict = Depends(require_admin),
) -> SessionResponse:
    response.headers["Cache-Control"] = "no-store"

    return SessionResponse(
        authenticated=True,
        username=session["sub"],
        csrf_token=session["csrf"],
    )


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    session: dict = Depends(require_csrf),
) -> dict:
    response.delete_cookie(
        key=SESSION_COOKIE,
        **cookie_options(request),
    )

    response.headers["Cache-Control"] = "no-store"

    return {
        "success": True,
        "message": "Logged out successfully.",
    }
