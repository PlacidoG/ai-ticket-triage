
from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.ticket import Ticket


class AgentAction(Base, TimestampMixin):
    __tablename__ = "agent_actions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    ticket_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
    )

    agent_id: Mapped[str] = mapped_column(
        String(100),     # plain string for now - no users table
        nullable=False,
    )
    
    action_type: Mapped[str] = mapped_column(
         String(20),    #"override or status change"
            nullable=False,
    )

    override_field: Mapped[str | None] = mapped_column(
        String(30),      # which field was changed (severoty, category, etc.)
        nullable=True,   # only populated if action_type=override
    )

    old_value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True)
    new_value: Mapped[str] = mapped_column(
        Text,
        nullable=False)
    
    # ---- Relationship ----
    ticket: Mapped["Ticket"] = relationship(
        back_populates="agent_actions",
    )
