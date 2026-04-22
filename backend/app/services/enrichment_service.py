
from __future__ import annotations

import logging
import time


from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.ai_enrichment import AIEnrichment
from app.models.ticket import Ticket
from app.models.enums import TicketStatus
from app.services.ai_service import enrich_ticket


logger = logging.getLogger(__name__)



def run_enrichment(ticket_id) -> None:
    """Background task: call Claude, store enrichment, update ticket status.

    This runs OUTSIDE the request lifecycle, so it creates its own
    database session. If enrichment fails, the ticket stays as 'new'
    with no enrichment — the agent can still triage it manually.
    """
    db: Session = SessionLocal()


    try: 
        ticket = db.get(Ticket, ticket_id)
        if not ticket:
            logger.error("Enrichment skipped: ticket %s not found", ticket_id)
            return
        
         # Skip if already enriched (safety check for duplicate triggers)
        if ticket.enrichment is not None:
            logger.info("Ticket %s already enriched, skipping", ticket_id)
            return
        
        logger.info("Starting enrichment for ticket %s: %s", ticket_id, ticket.title)


        # --- Call Claude with duration tracking ---
        start_time = time.time()


        result = enrich_ticket(ticket.title, ticket.description)

        duration = time.time() - start_time
        logger.info(
            "Enrichment completed in %.2fs - %s/$s (%.0f%% confidence)",
            duration,
            result["severity"],
            result["category"],
            result["confidence"] *100,
        )


        # --- Store enrichment in database ---
        enrichment = AIEnrichment(
            ticket_id=ticket.id,
            severity=result["severity"],
            category=result["category"],
            summary=result["summary"],
            suggested_response=result["suggested_response"],
            confidence=result["confidence"],
            model_used=result["model_used"],
            prompt_version=result["prompt_version"],
            tokens_in=result["tokens_in"],
            tokens_out=result["tokens_out"],
            estimated_cost=result["estimated_cost"],
            raw_response=result["raw_response"],
        )
        db.add(enrichment)


        # --- Update ticket status to triaged ---
        ticket.status = TicketStatus.TRIAGED.value
        db.commit()

        logger.info("Ticket %s enriched and triaged successfully", ticket_id)

    except Exception as e:
        db.rollback()
        logger.error(
            "Enrichment failed for ticket %s: %s. "
            "Ticket remains as 'new' for manual triage.",
            ticket_id, str(e),
        )

    
    finally:
        db.close()
