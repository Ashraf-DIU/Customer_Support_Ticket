import logging
from typing import Optional, Tuple

import httpx

from ..config import settings
from ..models import Ticket

log = logging.getLogger("supportiq.reply")

CATEGORY_LINES = {
    "Technical issue": "Our technical team will review the details you shared. To speed things up, please send the exact error message, when it started, and the steps that led to it.",
    "Billing inquiry": "Our billing team will review the charges on your account and come back to you with what they find.",
    "Refund request": "Our billing team will review your order and the refund eligibility, and let you know the next steps.",
    "Cancellation request": "We will review your cancellation request and confirm the options available on your account.",
    "Product inquiry": "Our product team will get you the details you need. If you have a specific use case, share it and we will tailor the answer.",
}


def template_reply(t: Ticket) -> str:
    about = f" about your {t.product}" if t.product else ""
    line = CATEGORY_LINES.get(t.category, "Our team will review your request and follow up shortly.")
    urgency = " We have marked this as high priority." if t.priority in ("High", "Critical") else ""
    return (
        f"Hi {t.customer_name},\n\n"
        f"Thank you for contacting us{about}. I'm sorry for the trouble with {t.topic.lower()}. "
        f"{line}{urgency}\n\n"
        "Best regards,\nSupport Team"
    )


def llm_reply(t: Ticket) -> Optional[str]:
    if not settings.llm_api_key:
        return None
    system = (
        "You draft customer support replies that a human agent will review before sending. "
        "Be warm, concise (under 140 words), and specific to the ticket. Do not promise refunds, "
        "credits, or timelines, and do not invent facts. Ask for any missing information. Sign off as 'Support Team'."
    )
    user = (
        f"Customer: {t.customer_name}\nProduct: {t.product or 'unknown'}\nCategory: {t.category}\n"
        f"Priority: {t.priority}\nSubject: {t.subject}\nMessage: {t.description}"
    )
    try:
        r = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": settings.llm_api_key, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            json={"model": settings.llm_model, "max_tokens": 400, "system": system,
                  "messages": [{"role": "user", "content": user}]},
            timeout=30,
        )
        r.raise_for_status()
        return "".join(b.get("text", "") for b in r.json().get("content", [])).strip() or None
    except Exception as exc:  # noqa: BLE001
        log.warning("LLM reply failed, using template: %s", exc)
        return None


def generate_reply(t: Ticket) -> Tuple[str, str]:
    text = llm_reply(t)
    return (text, "llm") if text else (template_reply(t), "template")
