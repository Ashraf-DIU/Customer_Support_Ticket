"""Transparent business rules: priority escalation and department routing."""
from typing import Tuple

PRIORITY_ORDER = ["Low", "Medium", "High", "Critical"]

CRITICAL_PHRASES = ("data loss", "lost all my data", "lost my data", "security breach", "hacked",
                    "unauthorized", "charged twice", "double charged", "production down")
HIGH_PHRASES = ("urgent", "asap", "immediately", "not working at all", "still waiting", "no response",
                "contacted support twice", "third time", "deadline", "emergency")

CATEGORY_DEPARTMENT = {
    "Technical issue": "Technical Support",
    "Billing inquiry": "Billing Support",
    "Refund request": "Billing Support",
    "Cancellation request": "Retention Team",
    "Product inquiry": "Sales & Product",
}
TOPIC_DEPARTMENT = {
    "Payment issue": "Billing Support",
    "Refund request": "Billing Support",
    "Account access": "Account Security",
    "Delivery problem": "Logistics",
    "Cancellation request": "Retention Team",
    "Product recommendation": "Sales & Product",
    "Product compatibility": "Sales & Product",
}


def escalate_priority(model_priority: str, text: str) -> Tuple[str, str]:
    """Raise (never lower) the model's priority when the customer states explicit urgency."""
    low = text.lower()
    floor, reason = None, "Model prediction"
    for p in CRITICAL_PHRASES:
        if p in low:
            floor, reason = "Critical", f'Escalated by rule: mentions "{p}"'
            break
    if floor is None:
        for p in HIGH_PHRASES:
            if p in low:
                floor, reason = "High", f'Escalated by rule: mentions "{p}"'
                break
    if floor and PRIORITY_ORDER.index(floor) > PRIORITY_ORDER.index(model_priority):
        return floor, reason
    return model_priority, "Model prediction"


def route_department(category: str, topic: str) -> str:
    return TOPIC_DEPARTMENT.get(topic) or CATEGORY_DEPARTMENT.get(category, "General Support")
