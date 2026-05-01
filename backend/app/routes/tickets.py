from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.errors import InvalidStatusError, TicketNotFoundError
from app.models.ticket import Ticket
from app.models.enums import TicketStatus
from app.schemas.ticket import (
    TicketCreate,
    TicketDetailResponse,
    TicketListResponse,
    TicketListItem,
    TicketResponse,
    TicketUpdate,
)

from app.services.enrichment_service import run_enrichment

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.post("", response_model=TicketResponse, status_code=201)
def create_ticket(
    payload: TicketCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db),
):
    """Create a ticket from the web form. Source is always 'web_form'.

    Returns the ticket immediately. AI enrichment runs in the background
    and updates the ticket status to 'triaged' when complete (~2-3 seconds).
    """

    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        submitter_email=payload.submitter_email,
        source="web_form",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    background_tasks.add_task(run_enrichment, ticket.id)

    
    return ticket


@router.get("", response_model=TicketListResponse)
def list_tickets(
    status: str | None = Query(None),
    severity: str | None = Query(None),
    category: str | None = Query(None),
    assigned_to: str | None = Query(None),
    order: str = Query("desc", description="Sort by created_at: 'desc' (newest first) or 'asc' (oldest first)"),
    after: uuid.UUID | None = Query(None, description="Cursor: ticket ID to start after"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List tickets with optional filters, sorting, and cursor-based pagination.

    Includes lightweight enrichment data (severity, category, confidence)
    for badge display in the list view.
    """
    from sqlalchemy import func
    from app.models.ai_enrichment import AIEnrichment

    # --- Base query with enrichment join ---
    base_query = (
        select(Ticket)
        .outerjoin(Ticket.enrichment)
        .options(joinedload(Ticket.enrichment))
    )

    # --- Filters ---
    if status:
        base_query = base_query.where(Ticket.status == status)
    if assigned_to:
        base_query = base_query.where(Ticket.assigned_to == assigned_to)
    if severity:
        base_query = base_query.where(AIEnrichment.severity == severity)
    if category:
        base_query = base_query.where(AIEnrichment.category == category)

    # --- Total count (before pagination) ---
    count_query = select(func.count()).select_from(
        base_query.with_only_columns(Ticket.id).subquery()
    )
    total = db.execute(count_query).scalar() or 0

    # --- Sorting ---
    if order == "asc":
        base_query = base_query.order_by(Ticket.created_at.asc(), Ticket.id.asc())
    else:
        base_query = base_query.order_by(Ticket.created_at.desc(), Ticket.id.desc())

    # --- Cursor ---
    if after:
        cursor_ticket = db.get(Ticket, after)
        if cursor_ticket:
            if order == "asc":
                base_query = base_query.where(
                    (Ticket.created_at > cursor_ticket.created_at)
                    | (
                        (Ticket.created_at == cursor_ticket.created_at)
                        & (Ticket.id > cursor_ticket.id)
                    )
                )
            else:
                base_query = base_query.where(
                    (Ticket.created_at < cursor_ticket.created_at)
                    | (
                        (Ticket.created_at == cursor_ticket.created_at)
                        & (Ticket.id < cursor_ticket.id)
                    )
                )

    results = db.execute(base_query.limit(limit + 1)).scalars().unique().all()

    has_more = len(results) > limit
    tickets = results[:limit]
    next_cursor = tickets[-1].id if has_more and tickets else None

    # Build response with enrichment summary
    ticket_items = []
    for t in tickets:
        item = TicketListItem(
            id=t.id,
            title=t.title,
            description=t.description,
            status=t.status,
            source=t.source,
            submitter_email=t.submitter_email,
            assigned_to=t.assigned_to,
            created_at=t.created_at,
            updated_at=t.updated_at,
            severity=t.enrichment.severity if t.enrichment else None,
            category=t.enrichment.category if t.enrichment else None,
            confidence=t.enrichment.confidence if t.enrichment else None,
        )
        ticket_items.append(item)

    return TicketListResponse(
        tickets=ticket_items,
        next_cursor=next_cursor,
        has_more=has_more,
        total=total,
    )


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
def get_ticket(ticket_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a single ticket with its AI enrichment (if any)."""
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise TicketNotFoundError(ticket_id)
    return ticket


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: uuid.UUID,
    payload: TicketUpdate,
    db: Session = Depends(get_db),
):
    """Update ticket status and/or assignment.Logs status changes to audit trail."""
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise TicketNotFoundError(ticket_id)

    if payload.status is not None:
        valid = [s.value for s in TicketStatus]
        if payload.status not in valid:
            raise InvalidStatusError(payload.status, valid)
        
        old_status = ticket.status
        ticket.status = payload.status

        # Log status change in audit trail
        if old_status != payload.status:
            from app.models.agent_action import AgentAction
            action = AgentAction(
                ticket_id=ticket.id,
                agent_id=payload.agent_id or "system",
                action_type="status_change",
                override_field="status",
                old_value=old_status,
                new_value=payload.status,
            )
            db.add(action)

            
    if payload.assigned_to is not None:
        ticket.assigned_to = payload.assigned_to

    db.commit()
    db.refresh(ticket)
    return ticket