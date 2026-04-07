import uuid

from sqlalchemy import CheckConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import TicketStatus


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