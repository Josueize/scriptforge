import logging

import httpx
from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.models.schemas import (
    ApproveRequest,
    ApproveResponse,
    GenerateRequest,
    GenerateResponse,
)
from app.orchestrator.pipeline import ContentPipeline

# --------------------------------------------------
# Logging and router configuration
# --------------------------------------------------

logger = logging.getLogger("scriptforge.routes")

router = APIRouter()

pipeline = ContentPipeline()


# --------------------------------------------------
# Generate content using the AI pipeline
# --------------------------------------------------


@router.post("/generate", response_model=GenerateResponse)
async def generate_content(
    request: GenerateRequest,
) -> GenerateResponse:
    try:
        return await pipeline.run(request)

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        logger.error("Pipeline error: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Content generation failed. Please try again.",
        ) from exc

    except Exception as exc:
        # Catch unexpected failures at the API boundary.
        logger.exception("Unexpected pipeline error")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred.",
        ) from exc


# --------------------------------------------------
# Approve content and trigger n8n automation
# --------------------------------------------------


@router.post("/approve", response_model=ApproveResponse)
async def approve_content(
    request: ApproveRequest,
) -> ApproveResponse:

    # Approval succeeds even when automation is not configured.
    if not settings.n8n_webhook_url:
        logger.info(
            "Content approved without automation | content_id=%s",
            request.content_id,
        )

        return ApproveResponse(
            success=True,
            message="Approved. Automation not configured.",
        )

    payload = {
        "content_id": request.content_id,
        "platforms": request.platforms,
        "event": "content_approved",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                settings.n8n_webhook_url,
                json=payload,
            )

            # Raise an exception for HTTP 4xx and 5xx responses.
            response.raise_for_status()

    except httpx.TimeoutException:
        logger.warning(
            "n8n webhook timed out | content_id=%s",
            request.content_id,
        )

        return ApproveResponse(
            success=False,
            message=(
                "Content approved, but the automation request timed out. Check n8n."
            ),
        )

    except httpx.HTTPStatusError as exc:
        logger.error(
            "n8n webhook HTTP error | content_id=%s | status=%s",
            request.content_id,
            exc.response.status_code,
        )

        return ApproveResponse(
            success=False,
            message=(
                "Content approved, but the automation webhook "
                "returned an error. Check n8n."
            ),
        )

    except httpx.RequestError as exc:
        logger.error(
            "n8n webhook connection error | content_id=%s | error=%s",
            request.content_id,
            type(exc).__name__,
        )

        return ApproveResponse(
            success=False,
            message=(
                "Content approved, but the automation service could not be reached."
            ),
        )

    logger.info(
        "n8n webhook accepted | content_id=%s",
        request.content_id,
    )

    return ApproveResponse(
        success=True,
        message="Approved. Automation pipeline triggered.",
    )
