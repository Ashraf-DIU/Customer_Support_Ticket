from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_name: Mapped[str] = mapped_column(String(120), default="Customer")
    customer_email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    product: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    channel: Mapped[str] = mapped_column(String(30), default="Web form")
    subject: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)

    category: Mapped[str] = mapped_column(String(60), index=True)
    category_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    priority: Mapped[str] = mapped_column(String(20), index=True)
    priority_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    priority_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    topic: Mapped[str] = mapped_column(String(80))
    topic_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    sentiment: Mapped[str] = mapped_column(String(20), index=True)
    sentiment_score: Mapped[float] = mapped_column(Float, default=0.0)
    department: Mapped[str] = mapped_column(String(60), index=True)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False)
    model_version: Mapped[str] = mapped_column(String(60), default="")

    status: Mapped[str] = mapped_column(String(30), default="Open", index=True)
    suggested_reply: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reply_source: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    @property
    def code(self) -> str:
        return f"TKT-{self.id:05d}"
