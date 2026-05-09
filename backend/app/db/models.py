from datetime import datetime
from sqlalchemy import String, DateTime, Integer, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class GeneratedContent(Base):
    __tablename__ = "generated_content"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    idea: Mapped[str] = mapped_column(String(500))
    tone: Mapped[str] = mapped_column(String(20))
    length: Mapped[str] = mapped_column(String(5))
    script: Mapped[str] = mapped_column(String)
    platforms: Mapped[dict] = mapped_column(JSON)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)