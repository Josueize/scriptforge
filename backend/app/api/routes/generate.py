
import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.auth import require_csrf
from app.core.config import settings
from app.db.database import get_db
from app.db.models import GeneratedContent
from app.models.schemas import (
    ApproveRequest,
    ApproveResponse,
    GenerateRequest,
    GenerateResponse,
)
from app.orchestrator.pipeline import ContentPipeline

# ==================================================
# INITIALIZATION
# ==================================================

logger = logging.getLogger("scriptforge.routes")

router = APIRouter()

pipeline = ContentPipeline()


# ==================================================
# GENERATE CONTENT
#
# Administrator authentication required
# CSRF verification required
#
# OpenAI -> Claude -> PostgreSQL
# ==================================================

@router.post(
    "/generate",
    response_model=GenerateResponse,
    dependencies=[Depends(require_csrf)],
)
async def generate_content(
    request: GenerateRequest,
    db: AsyncSession = Depends(get_db),
) -> GenerateResponse:

    # ----------------------------------------------
    # STEP 1: GENERATE CONTENT USING AI
    # ----------------------------------------------

    try:
        result = await pipeline.run(request)

    except ValueError as exc:
        logger.warning(
            "Content validation failed | error_type=%s",
            type(exc).__name__,
        )

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        logger.exception(
            "AI generation pipeline failed | error_type=%s",
            type(exc).__name__,
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Content generation failed. "
                "Please try again."
            ),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected content generation error"
        )

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred.",
        ) from exc

    # ----------------------------------------------
    # STEP 2: PREPARE DATABASE RECORD
    # ----------------------------------------------

    record = GeneratedContent(
        id=result.id,
        idea=request.idea,
        tone=request.tone,
        length=request.length,
        script=result.script,
        platforms={
            "items": [
                platform.model_dump()
                for platform in result.platforms
            ]
        },
        tokens_used=result.metadata.tokens_used,
        status="pending",
    )

    # ----------------------------------------------
    # STEP 3: SAVE CONTENT TO POSTGRESQL
    # ----------------------------------------------

    try:
        db.add(record)

        await db.commit()

    except SQLAlchemyError as exc:
        await db.rollback()

        logger.exception(
            "Database persistence failed | content_id=%s",
            result.id,
        )

        raise HTTPException(
            status_code=500,
            detail="Generated content could not be saved.",
        ) from exc

    # ----------------------------------------------
    # STEP 4: LOG SUCCESS
    # ----------------------------------------------

    logger.info(
        "Generated content saved | content_id=%s",
        result.id,
    )

    # ----------------------------------------------
    # STEP 5: RETURN GENERATED CONTENT
    # ----------------------------------------------

    return result


# ==================================================
# APPROVE CONTENT
#
# Administrator authentication required
# CSRF verification required
#
# PostgreSQL -> n8n -> Google Docs
# ==================================================

@router.post(
    "/approve",
    response_model=ApproveResponse,
    dependencies=[Depends(require_csrf)],
)
async def approve_content(
    request: ApproveRequest,
    db: AsyncSession = Depends(get_db),
) -> ApproveResponse:

    content_id = request.content_id

    # ----------------------------------------------
    # STEP 1: VERIFY N8N CONFIGURATION
    # ----------------------------------------------

    if (
        not settings.n8n_webhook_url
        or not settings.n8n_webhook_token
    ):
        logger.error(
            "n8n webhook configuration is missing"
        )

        return ApproveResponse(
            success=False,
            message=(
                "n8n automation is not configured. "
                "Please contact the administrator."
            ),
        )

    # ----------------------------------------------
    # STEP 2: FETCH CONTENT FROM POSTGRESQL
    # ----------------------------------------------

    try:
        record = await db.get(
            GeneratedContent,
            content_id,
        )

    except SQLAlchemyError as exc:
        logger.exception(
            "Database retrieval failed | content_id=%s",
            content_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve generated content.",
        ) from exc

    # ----------------------------------------------
    # STEP 3: VERIFY CONTENT EXISTS
    # ----------------------------------------------

    if record is None:
        logger.warning(
            "Approval requested for missing content | "
            "content_id=%s",
            content_id,
        )

        raise HTTPException(
            status_code=404,
            detail="Generated content not found.",
        )

    # ----------------------------------------------
    # STEP 4: CHECK APPROVAL STATUS
    # ----------------------------------------------

    if record.status == "approved":
        logger.info(
            "Content already approved | content_id=%s",
            content_id,
        )

        return ApproveResponse(
            success=True,
            message=(
                "Content was already approved. "
                "No additional webhook was sent."
            ),
        )

    if record.status != "pending":
        logger.warning(
            "Invalid approval status | "
            "content_id=%s | status=%s",
            content_id,
            record.status,
        )

        raise HTTPException(
            status_code=409,
            detail="Content is not awaiting approval.",
        )

    # ----------------------------------------------
    # STEP 5: VALIDATE SAVED SCRIPT
    # ----------------------------------------------

    if not record.script or not record.script.strip():
        logger.warning(
            "Approval attempted with empty script | "
            "content_id=%s",
            content_id,
        )

        raise HTTPException(
            status_code=422,
            detail="Generated content has no script.",
        )

    # ----------------------------------------------
    # STEP 6: PREPARE N8N PAYLOAD
    # ----------------------------------------------

    payload = {
        "title": f"ScriptForge - {record.idea}",
        "status": "approved",
        "script": record.script,
    }

    logger.info(
        "Sending approved content to n8n | "
        "content_id=%s",
        content_id,
    )

    # ----------------------------------------------
    # STEP 7: SEND APPROVAL TO N8N
    # ----------------------------------------------

    try:
        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=False,
        ) as client:

            response = await client.post(
                settings.n8n_webhook_url,
                json=payload,
                headers={
                    "X-ScriptForge-Key": (
                        settings.n8n_webhook_token
                    ),
                    "Content-Type": "application/json",
                },
            )

            response.raise_for_status()

    # ----------------------------------------------
    # STEP 8: HANDLE TIMEOUT ERRORS
    # ----------------------------------------------

    except httpx.TimeoutException:
        logger.warning(
            "n8n webhook timed out | content_id=%s",
            content_id,
        )

        return ApproveResponse(
            success=False,
            message=(
                "n8n request timed out. "
                "Check n8n execution history "
                "before retrying."
            ),
        )

    # ----------------------------------------------
    # STEP 9: HANDLE N8N HTTP ERRORS
    # ----------------------------------------------

    except httpx.HTTPStatusError as exc:
        logger.error(
            "n8n returned HTTP %s | content_id=%s",
            exc.response.status_code,
            content_id,
        )

        return ApproveResponse(
            success=False,
            message=(
                "n8n rejected the approval request. "
                "Check the webhook configuration."
            ),
        )

    # ----------------------------------------------
    # STEP 10: HANDLE NETWORK ERRORS
    # ----------------------------------------------

    except httpx.RequestError as exc:
        logger.error(
            "Unable to contact n8n | "
            "content_id=%s | error_type=%s",
            content_id,
            type(exc).__name__,
        )

        return ApproveResponse(
            success=False,
            message=(
                "Unable to contact the automation service. "
                "Check n8n before retrying."
            ),
        )

    # ----------------------------------------------
    # STEP 11: UPDATE CONTENT STATUS
    # ----------------------------------------------

    try:
        record.status = "approved"

        await db.commit()

    except SQLAlchemyError as exc:
        await db.rollback()

        logger.exception(
            "Approval status update failed | "
            "content_id=%s",
            content_id,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "n8n accepted the request, but "
                "the database update failed. "
                "Check n8n before retrying."
            ),
        ) from exc

    # ----------------------------------------------
    # STEP 12: LOG APPROVAL
    # ----------------------------------------------

    logger.info(
        "Content approved and webhook accepted | "
        "content_id=%s",
        content_id,
    )

    # ----------------------------------------------
    # STEP 13: RETURN SUCCESS RESPONSE
    # ----------------------------------------------

    return ApproveResponse(
        success=True,
        message=(
            "Content approved and sent to n8n. "
            "Check n8n execution history to "
            "verify Google Docs creation."
        ),
    )
