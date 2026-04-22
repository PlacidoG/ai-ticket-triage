
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.ticket import Ticket

class AIEnrichment(Base, TimestampMixin):
    __tablename__ = "ai_enrichments"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    ticket_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tickets.id", ondelete="CASCADE"),
        unique=True,  # enforces one-to-one relationship at database level
        nullable=False,
        )
    

    # ---- AI output fields ----
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    suggested_response: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(
        Numeric(4, 3),
        nullable=False,
    )
    model_used: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # --- Obserability fields ---
    prompt_version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="v1.0",
    )
    tokens_in: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tokens_out: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_cost: Mapped[float] = mapped_column(
        Numeric(10,6),   # e.g. 0.003450
        nullable=False,
        default=0.0,
    )
    raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)


    # ---- Relationships ----
    ticket: Mapped["Ticket"] = relationship(
        back_populates="enrichment",
    )