from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import TicketStatus, TicketSource

if TYPE_CHECKING:
    from app.models.ai_enrichment import AIEnrichment
    from app.models.agent_action import AgentAction

class Ticket(Base, TimestampMixin):
    __tablename__ = "tickets"
    __table_args__=(
        CheckConstraint(
            "status IN ('new', 'triaged', 'in_progress', "
            "'waiting_on_customer', 'resolved', 'closed')",
            name="chk_ticket_status",
            ),
    )


    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str]= mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(35),
        default=TicketStatus.NEW.value,
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
    String(20),
    default=TicketSource.WEB_FORM.value,
    nullable=False,
    )

    submitter_email: Mapped[str | None] = mapped_column(
    String(255),
    nullable=True,  # API-sourced tickets might not have a submitter
    )

    assigned_to: Mapped[str | None] = mapped_column(
    String(100),
    nullable=True,   # null = unassigned, string = agent_id who owns it
    )


# Relationships
    enrichment: Mapped["AIEnrichment | None"] = relationship(
        back_populates="ticket",
        uselist=False,    #one-to-one relationship. Each ticket gets exactly one AI enrichment.
        cascade="all, delete-orphan",
    )
    agent_actions: Mapped[list["AgentAction"]] = relationship(
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="AgentAction.created_at.desc()",
    )