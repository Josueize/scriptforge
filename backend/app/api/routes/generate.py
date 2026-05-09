import logging
from fastapi import APIRouter, HTTPException

from app.models.schemas import GenerateRequest, GenerateResponse, ApproveRequest, ApproveResponse
from app.orchestrator.pipeline import ContentPipeline

logger = logging.getLogger("scriptforge.routes")
router = APIRouter()
pipeline = ContentPipeline()


@router.post("/generate", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest) -> GenerateResponse:
    try:
        return await pipeline.run(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.error("Pipeline error: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected pipeline error")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.") from exc


@router.post("/approve", response_model=ApproveResponse)
async def approve_content(request: ApproveRequest) -> ApproveResponse:
    import httpx
    from app.core.config import settings

    if not settings.n8n_webhook_url:
        return ApproveResponse(success=True, message="Approved. Automation not configured.")

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(settings.n8n_webhook_url, json={
                "content_id": request.content_id,
                "platforms": request.platforms,
                "event": "content_approved",
            })
        logger.info("n8n triggered | content_id=%s", request.content_id)
        return ApproveResponse(success=True, message="Approved. Automation pipeline triggered.")
    except Exception as exc:
        logger.error("n8n webhook failed: %s", exc)
        return ApproveResponse(success=True, message="Approved. Automation trigger failed — check n8n.")