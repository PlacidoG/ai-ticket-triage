from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

# Why two create schemas? 
# TicketCreate is for the web form (source is
# always web_form, set server-side). TicketIntake is for external systems
# that tell you what source they are. Keeps the contract clear for each consumer.

# --- Request schemas (what the client sends) ---

class TicketCreate(BaseModel):
    """Used by the web form: POST /api/tickets/"""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    submitter_email: str | None = Field(None, man_length=255)



class TicketIntake(BaseModel):
    """Used by external systems: POST /api/tickets/intake/
    Accepts extra fields that external systems provide"""

    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    source: str = Field(default="api", max_length=20)
    submitter_email: str | None = Field(None, max_length=255)


class TicketUpdate(BaseModel):
    """PATCH /api/tickets/{id} - update status or assignment"""
    status: str | None = None
    assigned_to: str | None = None


# --- Response schemas (what the API returns) ---

class TicketResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    status: str
    source: str
    submitter_email: str | None
    assigned_to: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}



class EnrichmentResponse(BaseModel):
    """AI enrichment data - only inlcuded on detail view"""
    id: uuid.UUID
    severity: str
    category: str
    summary: str
    suggested_response: str
    confidence: float
    model_used: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TicketDetailResponse(TicketResponse):
    """Single ticket with enrichment - used on detail view"""
    enrichment: EnrichmentResponse | None = None


class TicketListResponse(BaseModel):
    """Cursor-paginated list of tickets"""
    tickets: list[TicketResponse]
    next_cursor: uuid.UUID | None = None
    has_more: bool = False
