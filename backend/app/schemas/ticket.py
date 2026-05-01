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
    submitter_email: str | None = Field(None, max_length=255)



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
    agent_id: str | None = None


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


class TicketListItem(TicketResponse):
    """Ticket with lightweight enrichment summary for list views."""
    severity: str | None = None
    category: str | None = None
    confidence: float | None = None

    model_config = {"from_attributes": True, "protected_namespaces": ()}



class EnrichmentResponse(BaseModel):
    """AI enrichment data - only inlcuded on detail view"""
    id: uuid.UUID
    severity: str
    category: str
    summary: str
    suggested_response: str
    confidence: float
    model_used: str
    prompt_version: str
    tokens_in: int
    tokens_out: int
    estimated_cost: float
    raw_response: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True, "pro_namespaces": ()}
    


class TicketDetailResponse(TicketResponse):
    """Single ticket with enrichment - used on detail view"""
    enrichment: EnrichmentResponse | None = None


class TicketListResponse(BaseModel):
    """Cursor-paginated list of tickets"""
    tickets: list[TicketListItem]
    next_cursor: uuid.UUID | None = None
    has_more: bool = False
    total: int = 0


# --- Override schemas ---

class OverrideRequest(BaseModel):
    """Agent overrides an AI enrichment field"""
    field: str = Field(..., description="Field to override: severity, category, or suggested_response")
    new_value: str = Field(..., min_length=1)
    agent_id: str = Field(..., min_length=1, max_length=100)


class OverrideResponse(BaseModel):
    """Confirmation of the override."""
    ticket_id: uuid.UUID
    field: str
    old_value: str
    new_value: str
    agent_id: str

    model_config = {"from_attributes": True}


# --- Dashboard schemas ---

class DashboardSummary(BaseModel):
    """Top-level metrics for dashboard cards."""
    total_tickets: int
    open_tickets: int
    critical_high_tickets: int
    ai_accuracy_rate: float
    avg_enrichment_cost: float
    total_enrichment_cost: float
    total_enriched: int


class TicketByField(BaseModel):
    """Generic count-by-field structure for charts."""
    label: str
    count: int


class OverrideBreakdown(BaseModel):
    """How often each field gets overrridden."""
    field: str
    override_count: int
    total_enriched: int
    accuracy_rate: float


class DashboardCharts(BaseModel):
    """Aggregated data for dashboard charts."""
    by_severity: list[TicketByField]
    by_category: list[TicketByField]
    by_status: list[TicketByField]
    override_breakdown: list[OverrideBreakdown]
