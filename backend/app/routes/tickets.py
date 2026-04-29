from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import InvalidStatusError, TicketNotFoundError
from app.models.ticket import Ticket
from app.models.enums import TicketStatus
from app.schemas.ticket import (
    TicketCreate,
    TicketDetailResponse,
    TicketListResponse,
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
    after: uuid.UUID | None = Query(None, description="Cursor: ticket ID to start after"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List tickets with optional filters and cursor-based pagination.

    Cursor logic: tickets are sorted by created_at DESC.
    Pass `after=<ticket_id>` to get the next page — returns tickets
    created *before* that ticket.
    """
    query = select(Ticket).order_by(Ticket.created_at.desc(), Ticket.id.desc())

    # --- Filters ---
    if status:
        query = query.where(Ticket.status == status)
    if assigned_to:
        query = query.where(Ticket.assigned_to == assigned_to)

    # Severity and category live on AIEnrichment, not Ticket.
    # We'll add join-based filtering on Day 5 when enrichment exists.
    # For now, these params are accepted but ignored so the API
    # contract is stable for the frontend.

    # --- Cursor ---
    if after:
        cursor_ticket = db.get(Ticket, after)
        if cursor_ticket:
            query = query.where(
                (Ticket.created_at < cursor_ticket.created_at)
                | (
                    (Ticket.created_at == cursor_ticket.created_at)
                    & (Ticket.id < cursor_ticket.id)
                )
            )

    # Fetch one extra to check if there are more results
    results = db.execute(query.limit(limit + 1)).scalars().all()

    has_more = len(results) > limit
    tickets = results[:limit]
    next_cursor = tickets[-1].id if has_more and tickets else None

    return TicketListResponse(
        tickets=tickets,
        next_cursor=next_cursor,
        has_more=has_more,
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