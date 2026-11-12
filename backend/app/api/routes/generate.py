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


logger = logging.getLogger("scriptforge.routes")
router = APIRouter()
pipeline = ContentPipeline()


# --------------------------------------------------
# Generate content using OpenAI and Claude
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
        logger.error(
            "Content pipeline failed: %s",
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=502,
            detail="Content generation failed. Please try again.",
        ) from exc

    except Exception as exc:
        # Catch unexpected errors at the API boundary.
        logger.exception("Unexpected content generation error")
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

    # Check that n8n is configured securely.
    if not settings.n8n_webhook_url or not settings.n8n_webhook_token:
        logger.warning("n8n webhook URL or authentication token missing")

        return ApproveResponse(
            success=False,
            message=("Automation is not configured. Please contact the administrator."),
        )

    # Prepare the approval event sent to n8n.
    payload = {
        "content_id": request.content_id,
        "platforms": request.platforms,
        "event": "content_approved",
    }

    # Send authenticated request to n8n.
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                settings.n8n_webhook_url,
                json=payload,
                headers={
                    "X-ScriptForge-Token": (settings.n8n_webhook_token),
                },
            )

            # Raise errors for HTTP 4xx or 5xx.
            response.raise_for_status()

    except httpx.TimeoutException:
        logger.warning(
            "n8n webhook timeout | content_id=%s",
            request.content_id,
        )

        return ApproveResponse(
            success=False,
            message=(
                "Approval request received, but the automation timed out. Check n8n."
            ),
        )

    except httpx.HTTPStatusError as exc:
        logger.error(
            "n8n webhook returned HTTP %s | content_id=%s",
            exc.response.status_code,
            request.content_id,
        )

        return ApproveResponse(
            success=False,
            message=("Approval request received, but n8n returned an error."),
        )

    except httpx.RequestError as exc:
        logger.error(
            "n8n connection failed | content_id=%s | error=%s",
            request.content_id,
            type(exc).__name__,
        )

        return ApproveResponse(
            success=False,
            message=(
                "Approval request received, but the "
                "automation service could not be reached."
            ),
        )

    logger.info(
        "n8n webhook accepted | content_id=%s",
        request.content_id,
    )

    return ApproveResponse(
        success=True,
        message="Content approved. Automation request accepted by n8n.",
    )
