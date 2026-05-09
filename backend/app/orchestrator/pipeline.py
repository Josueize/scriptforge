import asyncio
import logging
import uuid
from datetime import datetime, timezone

from app.services.openai_service import OpenAIService
from app.services.claude_service import ClaudeService
from app.models.schemas import GenerateRequest, GenerateResponse, PlatformContent, GenerateMetadata

logger = logging.getLogger("scriptforge.pipeline")


class ContentPipeline:
    """
    Full AI orchestration pipeline:

        User Input
            ↓
        OpenAI  →  Initial script generation
            ↓
        Claude  →  Tone refinement & quality pass
            ↓
        Validation
            ↓
        Claude  →  Parallel platform formatting (asyncio.gather)
            ↓
        GenerateResponse
    """

    def __init__(self) -> None:
        self._openai = OpenAIService()
        self._claude = ClaudeService()

    async def run(self, request: GenerateRequest) -> GenerateResponse:
        content_id = str(uuid.uuid4())
        total_tokens = 0

        logger.info("Pipeline started | id=%s | tone=%s | length=%s", content_id, request.tone, request.length)

        # Step 1: OpenAI — initial generation
        raw_script, tokens = await self._openai.generate_script(request.idea, request.tone, request.length)
        total_tokens += tokens

        # Step 2: Claude — tone refinement
        refined_script, tokens = await self._claude.refine_script(raw_script, request.tone)
        total_tokens += tokens

        # Step 3: Validate
        _validate_script(refined_script)

        # Step 4: Parallel platform formatting
        results = await asyncio.gather(
            *[self._claude.format_for_platform(refined_script, p, request.tone) for p in request.platforms],
            return_exceptions=True,
        )

        platforms: list[PlatformContent] = []
        for platform, result in zip(request.platforms, results):
            if isinstance(result, Exception):
                logger.error("Platform %s failed: %s", platform, result)
                continue
            content, tokens = result
            total_tokens += tokens
            platforms.append(PlatformContent(
                platform=platform,
                content=content,
                word_count=len(content.split()),
            ))

        logger.info("Pipeline complete | id=%s | total_tokens=%d", content_id, total_tokens)

        return GenerateResponse(
            id=content_id,
            script=refined_script,
            platforms=platforms,
            metadata=GenerateMetadata(
                tone=request.tone,
                length=request.length,
                generated_at=datetime.now(timezone.utc),
                tokens_used=total_tokens,
            ),
        )


def _validate_script(script: str) -> None:
    if not script or len(script.strip()) < 50:
        raise ValueError("Generated script is too short or empty — aborting pipeline.")