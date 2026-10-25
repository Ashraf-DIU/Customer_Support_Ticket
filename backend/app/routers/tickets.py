from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Ticket
from ..schemas import TicketIn, TicketList, TicketOut, TicketPatch
from ..services.reply import generate_reply
from ..services.ticket_service import build_ticket

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

PRIORITY_RANK = case(
    (Ticket.priority == "Critical", 4), (Ticket.priority == "High", 3),
    (Ticket.priority == "Medium", 2), else_=1,
)


def _get_or_404(db: Session, ticket_id: int) -> Ticket:
    t = db.get(Ticket, ticket_id)
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return t


@router.post("", response_model=TicketOut, status_code=201)
def create_ticket(body: TicketIn, db: Session = Depends(get_db)):
    ticket = build_ticket(body)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("", response_model=TicketList)
def list_tickets(
    q: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    department: Optional[str] = None,
    needs_review: Optional[bool] = None,
    open_only: bool = False,
    sort: str = Query("newest", pattern="^(newest|oldest|priority)$"),
    limit: int = Query(15, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(Ticket)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Ticket.subject.ilike(like), Ticket.description.ilike(like),
                              Ticket.customer_name.ilike(like)))
    if status:
        stmt = stmt.where(Ticket.status == status)
    if open_only:
        stmt = stmt.where(Ticket.status.in_(["Open", "In Progress", "Pending Customer"]))
    if priority:
        stmt = stmt.where(Ticket.priority == priority)
    if category:
        stmt = stmt.where(Ticket.category == category)
    if department:
        stmt = stmt.where(Ticket.department == department)
    if needs_review is not None:
        stmt = stmt.where(Ticket.needs_review == needs_review)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    if sort == "priority":
        stmt = stmt.order_by(PRIORITY_RANK.desc(), Ticket.created_at.desc())
    elif sort == "oldest":
        stmt = stmt.order_by(Ticket.created_at.asc())
    else:
        stmt = stmt.order_by(Ticket.created_at.desc())
    items = db.scalars(stmt.limit(limit).offset(offset)).all()
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, ticket_id)


@router.patch("/{ticket_id}", response_model=TicketOut)
def update_ticket(ticket_id: int, body: TicketPatch, db: Session = Depends(get_db)):
    t = _get_or_404(db, ticket_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(t, field, value)
    if body.priority is not None:
        t.priority_reason = "Set by agent"
    db.commit()
    db.refresh(t)
    return t


@router.delete("/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    db.delete(_get_or_404(db, ticket_id))
    db.commit()
    return Response(status_code=204)


@router.post("/{ticket_id}/suggest-reply", response_model=TicketOut)
def suggest_reply(ticket_id: int, db: Session = Depends(get_db)):
    t = _get_or_404(db, ticket_id)
    t.suggested_reply, t.reply_source = generate_reply(t)
    db.commit()
    db.refresh(t)
    return t
