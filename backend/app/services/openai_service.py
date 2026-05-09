import asyncio
import logging
from openai import AsyncOpenAI, APIError, RateLimitError

from app.core.config import settings

logger = logging.getLogger("scriptforge.openai")

WORD_TARGETS = {"1": "130-150", "3": "420-450", "5": "690-740", "10": "1380-1450"}

TONE_DIRECTIONS = {
    "Dramatic":  "Tense, cinematic. Short punchy sentences. Vivid language. Think prestige documentary.",
    "Neutral":   "Clear, balanced, journalistic. Accuracy over flair. Think BBC educational explainer.",
    "Uplifting": "Warm, inspiring, forward-looking. Close on hope or human agency. Think TED Talk.",
}


class OpenAIService:
    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate_script(self, idea: str, tone: str, length: str) -> tuple[str, int]:
        for attempt in range(1, settings.max_retries + 1):
            try:
                response = await self._client.chat.completions.create(
                    model=settings.openai_model,
                    max_tokens=2048,
                    messages=[
                        {"role": "system", "content": self._system_prompt()},
                        {"role": "user", "content": self._user_prompt(idea, tone, length)},
                    ],
                    timeout=settings.request_timeout,
                )
                script = response.choices[0].message.content or ""
                tokens = response.usage.total_tokens if response.usage else 0
                logger.info("OpenAI complete | tokens=%d | attempt=%d", tokens, attempt)
                return script, tokens

            except RateLimitError:
                wait = 2 ** attempt
                logger.warning("OpenAI rate limited. Retrying in %ds", wait)
                await asyncio.sleep(wait)

            except APIError as exc:
                if attempt == settings.max_retries:
                    raise RuntimeError(f"OpenAI failed after {settings.max_retries} attempts: {exc}") from exc
                await asyncio.sleep(2 ** attempt)

        raise RuntimeError("OpenAI generation failed: max retries exceeded")

    def _system_prompt(self) -> str:
        return (
            "You are a professional video script writer. Write production-ready scripts "
            "with natural spoken language and strong narrative arcs.\n\n"
            "FORMAT:\n- Open with [HOOK]\n- Label sections with [SECTION NAME]\n"
            "- Close with [OUTRO]\n- End with: (Approx. word count: N words)"
        )

    def _user_prompt(self, idea: str, tone: str, length: str) -> str:
        return (
            f'Topic: "{idea}"\nTone: {tone}\n'
            f"Tone direction: {TONE_DIRECTIONS[tone]}\n"
            f"Target duration: {length} minute{'s' if int(length) > 1 else ''}\n"
            f"Target word count: {WORD_TARGETS[length]} words\n\nWrite the complete script now."
        )