import uuid
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    """Adds created_at and updated_at to any model that inherits this."""

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )



