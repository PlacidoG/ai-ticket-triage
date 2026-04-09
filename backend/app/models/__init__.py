# Alembic's autogenerate only detects models that are imported. 
# This file ensures all models are registered.

from app.models.base import Base
from app.models.ticket import Ticket
from app.models.ai_enrichment import AIEnrichment
from app.models.agent_action import AgentAction

__all__ = ["Base", "Ticket", "AIEnrichment", "AgentAction"]