from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

Priority = Literal["Low", "Medium", "High", "Critical"]
Status = Literal["Open", "In Progress", "Pending Customer", "Resolved", "Closed"]
Channel = Literal["Web form", "Email", "Chat", "Phone", "Social media"]


class PredictIn(BaseModel):
    subject: str = Field("", max_length=200)
    message: str = Field(..., min_length=10, max_length=5000)

    @field_validator("subject", "message")
    @classmethod
    def strip(cls, v: str) -> str:
        return v.strip()


class TicketIn(BaseModel):
    customer_name: str = Field("Customer", max_length=120)
    customer_email: Optional[str] = Field(None, max_length=200)
    product: Optional[str] = Field(None, max_length=120)
    channel: Channel = "Web form"
    subject: str = Field(..., min_length=3, max_length=200)
    message: str = Field(..., min_length=10, max_length=5000)

    @field_validator("customer_name", "subject", "message")
    @classmethod
    def strip(cls, v: str) -> str:
        return v.strip()


class Alternative(BaseModel):
    label: str
    confidence: float


class PredictionOut(BaseModel):
    category: str
    category_confidence: float
    category_alternatives: List[Alternative]
    priority: str
    priority_confidence: float
    priority_reason: str
    topic: str
    topic_confidence: float
    sentiment: str
    sentiment_score: float
    department: str
    needs_review: bool
    model_version: str


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    customer_name: str
    customer_email: Optional[str]
    product: Optional[str]
    channel: str
    subject: str
    description: str
    category: str
    category_confidence: float
    priority: str
    priority_confidence: float
    priority_reason: Optional[str]
    topic: str
    topic_confidence: float
    sentiment: str
    sentiment_score: float
    department: str
    needs_review: bool
    model_version: str
    status: str
    suggested_reply: Optional[str]
    reply_source: Optional[str]
    created_at: datetime
    updated_at: datetime


class TicketPatch(BaseModel):
    status: Optional[Status] = None
    priority: Optional[Priority] = None
    department: Optional[str] = Field(None, max_length=60)
    suggested_reply: Optional[str] = Field(None, max_length=5000)


class TicketList(BaseModel):
    items: List[TicketOut]
    total: int
    limit: int
    offset: int
