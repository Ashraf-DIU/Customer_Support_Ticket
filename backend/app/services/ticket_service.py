from ..models import Ticket
from ..schemas import TicketIn
from .prediction import predictor
from .reply import generate_reply


def build_ticket(data: TicketIn) -> Ticket:
    p = predictor.predict(data.subject, data.message)
    ticket = Ticket(
        customer_name=data.customer_name or "Customer",
        customer_email=data.customer_email,
        product=data.product,
        channel=data.channel,
        subject=data.subject,
        description=data.message,
        category=p["category"], category_confidence=p["category_confidence"],
        priority=p["priority"], priority_confidence=p["priority_confidence"], priority_reason=p["priority_reason"],
        topic=p["topic"], topic_confidence=p["topic_confidence"],
        sentiment=p["sentiment"], sentiment_score=p["sentiment_score"],
        department=p["department"], needs_review=p["needs_review"], model_version=p["model_version"],
        status="Open",
    )
    # Draft a reply now (template by default, LLM when configured)
    ticket.suggested_reply, ticket.reply_source = generate_reply(ticket)
    return ticket
