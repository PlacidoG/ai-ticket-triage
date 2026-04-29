
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import TicketNotFoundError
from app.models.agent_action import AgentAction
from app.models.enums import Severity, Category
from app.schemas.ticket import OverrideRequest, OverrideResponse

router = APIRouter(prefix="/api/tickets", tags=["overrides"])

# Fields that agents are allowed to override, with their valid values
OVERRIDABLE_FIELDS = {
    "severity": {s.value for s in Severity},
    "category": {c.value for c in Category},
    "suggested_response": None,  # any string is valid
}


@router.post("/{ticket_id}/override", response_model=OverrideResponse)
def override_enrichment(
    ticket_id: uuid.UUID,
    payload: OverrideRequest,
    db: Session = Depends(get_db),
):
    """Agent overrides an AI enrichment field.

    Validates the field name and new value, updates the enrichment
    record, and logs the action in agent_actions for the audit trail.
    """
    from app.models.ticket import Ticket

    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise TicketNotFoundError(ticket_id)

    if ticket.enrichment is None:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail={
                "error": "no_enrichment",
                "message": "Cannot override — this ticket has no AI enrichment yet",
            },
        )

    # --- Validate field name ---
    if payload.field not in OVERRIDABLE_FIELDS:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=422,
            detail={
                "error": "invalid_override_field",
                "message": f"'{payload.field}' is not overridable",
                "valid_fields": list(OVERRIDABLE_FIELDS.keys()),
            },
        )

    # --- Validate new value for constrained fields ---
    valid_values = OVERRIDABLE_FIELDS[payload.field]
    if valid_values is not None and payload.new_value not in valid_values:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=422,
            detail={
                "error": "invalid_override_value",
                "message": f"'{payload.new_value}' is not a valid {payload.field}",
                "valid_values": sorted(valid_values),
            },
        )

    # --- Get old value ---
    old_value = getattr(ticket.enrichment, payload.field)

    # --- Update enrichment record ---
    setattr(ticket.enrichment, payload.field, payload.new_value)

    # --- Log the override action ---
    action = AgentAction(
        ticket_id=ticket.id,
        agent_id=payload.agent_id,
        action_type="override",
        override_field=payload.field,
        old_value=str(old_value),
        new_value=payload.new_value,
    )
    db.add(action)
    db.commit()

    return OverrideResponse(
        ticket_id=ticket.id,
        field=payload.field,
        old_value=str(old_value),
        new_value=payload.new_value,
        agent_id=payload.agent_id,
    )


# """ #  Field validation: Only severity, category, and suggested_response
# # can be overridden. Summary and confidence are AI-only.
# # Value validation: Severity must be a valid severity enum value. Category
# # must be a valid category. Suggested response accepts any string.
# # getattr/setattr: Dynamically reads and writes the field on the
# # enrichment model. This avoids a giant if/elif chain.
# # Audit trail: Every override creates an AgentAction with the old
# # and new values  """