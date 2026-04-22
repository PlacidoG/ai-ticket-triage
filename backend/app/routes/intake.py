

from fastapi import APIRouter, BackgroundTasks, Depends, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ticket import Ticket
from app.schemas.ticket import TicketIntake, TicketResponse
from app.services.enrichment_service import run_enrichment

router = APIRouter(prefix="/api/intake", tags=["intake"])

# Placeholder API key — validates external callers.
# In production this would check against a DB or secrets manager.
INTAKE_API_KEY = "intake-dev-key-2026"


@router.post("", response_model=TicketResponse, status_code=201)
def ingest_ticket(
    payload: TicketIntake,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., description="API key for authentication"),
):
    """Ingest a ticket from an external system.

    Returns the ticket immediately. AI enrichment runs in the background.
    """

    if x_api_key != INTAKE_API_KEY:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid API key")

    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        source=payload.source,
        submitter_email=payload.submitter_email,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # Trigger async AI enrichment
    background_tasks.add_task(run_enrichment, ticket.id)


    return ticket

# "the system has a dedicated ingestion endpoint — external monitoring tools POST alerts directly into the triage pipeline via API key auth