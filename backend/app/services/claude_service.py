import asyncio
import logging
from anthropic import AsyncAnthropic, APIError, RateLimitError
from anthropic.types import TextBlock

from app.core.config import settings

logger = logging.getLogger("scriptforge.claude")

PLATFORM_FORMATS = {
    "linkedin":   "A professional LinkedIn post (200-250 words). Narrative arc, one clear CTA.",
    "twitter":    "A Twitter/X thread. Hook tweet (max 280 chars) + 5-7 follow-up tweets numbered [1/] etc.",
    "youtube":    "A YouTube Short script (45-60 seconds, ~100 words). Hook in first 3 seconds.",
    "newsletter": "A newsletter summary (250-300 words). Warm opener, 3 key insights, one actionable takeaway.",
    "blog":       "An SEO blog outline: H1 title, meta description (155 chars), 4-6 H2 sections with bullet notes, CTA.",
}


class ClaudeService:
    def __init__(self) -> None:
        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def refine_script(self, script: str, tone: str) -> tuple[str, int]:
        for attempt in range(1, settings.max_retries + 1):
            try:
                response = await self._client.messages.create(
                    model=settings.claude_model,
                    max_tokens=2048,
                    system=(
                        "You are a senior editorial director. Improve the script for tone consistency, "
                        "narrative flow, and spoken-word clarity. Keep structure and section labels. "
                        "Return only the improved script."
                    ),
                    messages=[{"role": "user", "content": f"Tone target: {tone}\n\nScript:\n\n{script}"}],
                    timeout=settings.request_timeout,
                )
                block = response.content[0]
                refined = block.text if isinstance(block, TextBlock) else ""
                tokens = response.usage.input_tokens + response.usage.output_tokens
                logger.info("Claude refinement complete | tokens=%d", tokens)
                return refined, tokens

            except RateLimitError:
                await asyncio.sleep(2 ** attempt)
            except APIError as exc:
                if attempt == settings.max_retries:
                    raise RuntimeError(f"Claude failed: {exc}") from exc
                await asyncio.sleep(2 ** attempt)

        raise RuntimeError("Claude refinement failed: max retries exceeded")

    async def format_for_platform(self, script: str, platform: str, tone: str) -> tuple[str, int]:
        for attempt in range(1, settings.max_retries + 1):
            try:
                response = await self._client.messages.create(
                    model=settings.claude_model,
                    max_tokens=1024,
                    system="You are a platform content specialist. Adapt the script to the format specified. Return only the formatted content.",
                    messages=[{"role": "user", "content": (
                        f"Format: {PLATFORM_FORMATS[platform]}\nTone: {tone}\n\nSource script:\n\n{script}"
                    )}],
                    timeout=settings.request_timeout,
                )
                block = response.content[0]
                content = block.text if isinstance(block, TextBlock) else ""
                tokens = response.usage.input_tokens + response.usage.output_tokens
                return content, tokens

            except (RateLimitError, APIError) as exc:
                if attempt == settings.max_retries:
                    raise RuntimeError(f"Platform formatting failed ({platform}): {exc}") from exc
                await asyncio.sleep(2 ** attempt)

        raise RuntimeError(f"Platform formatting failed ({platform}): max retries exceeded")