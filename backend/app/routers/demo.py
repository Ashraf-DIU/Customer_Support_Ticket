from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..schemas import TicketIn
from ..services.ticket_service import build_ticket

router = APIRouter(prefix="/api/demo", tags=["demo"])

SAMPLES = [
    ("Maya Chen", "GoPro Hero", "Email", "Payment deducted but order cancelled", "My payment was deducted but my order was cancelled. I have contacted support twice and nobody has resolved this issue. I need this fixed urgently."),
    ("Daniel Okoye", "Dell XPS", "Chat", "Laptop will not boot", "My Dell XPS shows a black screen after the logo and then restarts. I tried holding the power button and removing the battery but nothing works."),
    ("Priya Nair", "Canon EOS", "Web form", "Cancel my subscription", "I would like to cancel my subscription before the next billing date. Please confirm once it is done."),
    ("Lucas Meyer", "Sony Xperia", "Phone", "Is this compatible with my headset?", "Before I buy, can you tell me whether the Sony Xperia works with Bluetooth 5.2 headsets and supports aptX?"),
    ("Aisha Rahman", "Microsoft Surface", "Email", "Lost all my data after update", "After the latest update my Surface lost all my data including project files. This is a disaster and I have a deadline tomorrow."),
    ("Tom Becker", "Nest Thermostat", "Chat", "Refund for damaged item", "The Nest Thermostat arrived damaged and I would like a refund. Photos are attached."),
    ("Sara Lindqvist", "Amazon Echo", "Social media", "Cannot connect to Wi-Fi", "My Amazon Echo keeps disconnecting from Wi-Fi every few minutes. Resetting the router did not help."),
    ("Omar Haddad", "Apple AirPods", "Web form", "Locked out of my account", "I cannot log in to my account and the password reset email never arrives. Thanks for any help."),
]


@router.post("/seed")
def seed(db: Session = Depends(get_db)):
    if not settings.allow_demo_seed:
        raise HTTPException(status_code=403, detail="Demo seeding is disabled")
    for name, product, channel, subject, message in SAMPLES:
        db.add(build_ticket(TicketIn(customer_name=name, product=product, channel=channel, subject=subject, message=message)))
    db.commit()
    return {"created": len(SAMPLES)}
