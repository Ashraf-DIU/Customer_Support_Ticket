from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Ticket

router = APIRouter(prefix="/api", tags=["analytics"])
OPEN = ["Open", "In Progress", "Pending Customer"]


def _counts(db: Session, column) -> list:
    rows = db.execute(select(column, func.count()).group_by(column).order_by(func.count().desc())).all()
    return [{"label": r[0], "count": r[1]} for r in rows]


@router.get("/analytics")
def analytics(db: Session = Depends(get_db)):
    total = db.scalar(select(func.count(Ticket.id))) or 0
    open_n = db.scalar(select(func.count(Ticket.id)).where(Ticket.status.in_(OPEN))) or 0
    urgent = db.scalar(select(func.count(Ticket.id)).where(
        Ticket.priority.in_(["High", "Critical"]), Ticket.status.in_(OPEN))) or 0
    review = db.scalar(select(func.count(Ticket.id)).where(
        Ticket.needs_review.is_(True), Ticket.status.in_(OPEN))) or 0

    start = (datetime.now(timezone.utc) - timedelta(days=13)).replace(hour=0, minute=0, second=0, microsecond=0)
    created = db.scalars(select(Ticket.created_at).where(Ticket.created_at >= start)).all()
    per_day: dict = {}
    for c in created:
        key = c.date().isoformat()
        per_day[key] = per_day.get(key, 0) + 1
    daily = []
    for i in range(14):
        d = (start + timedelta(days=i)).date().isoformat()
        daily.append({"date": d, "count": per_day.get(d, 0)})

    return {
        "total": total, "open": open_n, "urgent_open": urgent, "needs_review": review,
        "by_category": _counts(db, Ticket.category),
        "by_priority": _counts(db, Ticket.priority),
        "by_sentiment": _counts(db, Ticket.sentiment),
        "by_department": _counts(db, Ticket.department),
        "by_status": _counts(db, Ticket.status),
        "daily": daily,
    }
