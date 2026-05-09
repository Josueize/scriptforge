from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

Tone = Literal["Dramatic", "Neutral", "Uplifting"]
Length = Literal["1", "3", "5", "10"]
Platform = Literal["linkedin", "twitter", "youtube", "newsletter", "blog"]


class GenerateRequest(BaseModel):
    idea: str = Field(..., min_length=3, max_length=500)
    tone: Tone
    length: Length
    platforms: list[Platform] = Field(..., min_length=1)


class PlatformContent(BaseModel):
    platform: Platform
    content: str
    word_count: int


class GenerateMetadata(BaseModel):
    tone: Tone
    length: Length
    generated_at: datetime
    tokens_used: int


class GenerateResponse(BaseModel):
    id: str
    script: str
    platforms: list[PlatformContent]
    metadata: GenerateMetadata


class ApproveRequest(BaseModel):
    content_id: str
    platforms: list[Platform]


class ApproveResponse(BaseModel):
    success: bool
    message: str