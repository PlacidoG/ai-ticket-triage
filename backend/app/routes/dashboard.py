
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ticket import Ticket
from app.models.ai_enrichment import AIEnrichment
from app.models.agent_action import AgentAction
from app.schemas.ticket import (
    DashboardCharts,
    DashboardSummary,
    OverrideBreakdown,
    TicketByField,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(db: Session = Depends(get_db)):
    """Dashboard card metrics - simple counts using ORM."""


    # Total tickets
    total_tickets = db.query(Ticket).count()

    # Open tickets (not resolved or closed)
    open_tickets = (
        db.query(Ticket)
        .filter(Ticket.status.notin_(["resolved", "closed"]))
        .count()
    )

    # Critical + High severity (from enrichment)
    critical_high_tickets = (
        db.query(AIEnrichment)
        .filter(AIEnrichment.severity.in_(["critical", "high"]))
        .count()
    )

    # Total enriched tickets
    total_enriched = db.query(AIEnrichment).count()

    # Total overrides (only field overrides, not status changes)
    total_overrides = (
        db.query(AgentAction)
        .filter(AgentAction.action_type == "override")
        .count()
    )

    # AI accuracy: % of enriched tickets with NO overrides 
    if total_enriched > 0:
        overridden_tickets = (
            db.query(AgentAction.ticket_id)
            .filter(AgentAction.action_type == "override")
            .count()
        )
        ai_accuracy_rate = round(
            (total_enriched - overridden_tickets) / total_enriched, 3
        )
    else:
        ai_accuracy_rate = 0.0

    # AI cost metrics (ORM is fine here - simple aggregation)
    from sqlalchemy import func
    cost_result = (
        db.query(
            func.coalesce(func.sum(AIEnrichment.estimated_cost), 0),
            func.coalesce(func.avg(AIEnrichment.estimated_cost), 0),
        ).first()
    )
    total_cost = float(cost_result[0])
    avg_cost = float(cost_result[1])


    return DashboardSummary(
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        critical_high_tickets=critical_high_tickets,
        ai_accuracy_rate=ai_accuracy_rate,
        avg_enrichment_cost=round(avg_cost, 6),
        total_enrichment_cost=round(total_cost, 6),
        total_enriched=total_enriched,
    )

@router.get("/charts", response_model=DashboardCharts)
def get_charts(db: Session = Depends(get_db)):
    """Dashboard chart data - complex aggregations using raw SQL.

    Raw SQL is used here because these GROUP BY queries with JOINs
    are cleaner and more performant expressed directly in SQL than
    through the ORM query builder.
    """

    # --- Tickets by severity (JOIN to enrichments) ---
    severity_rows = db.execute(text("""
        SELECT e.severity AS label, COUNT(*) AS count
        FROM ai_enrichments e
        GROUP BY e.severity
        ORDER BY
            CASE e.severity
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                WHEN 'low' THEN 4
            END
    """)).fetchall()

    # --- Tickets by category ---
    category_rows = db.execute(text("""
        SELECT e.category AS label, COUNT(*) AS count
        FROM ai_enrichments e
        GROUP BY e.category
        ORDER BY count DESC
    """)).fetchall()

    # --- Tickets by status ---
    status_rows = db.execute(text("""
        SELECT t.status AS label, COUNT(*) AS count
        FROM tickets t
        GROUP BY t.status
        ORDER BY
            CASE t.status
                WHEN 'new' THEN 1
                WHEN 'triaged' THEN 2
                WHEN 'in_progress' THEN 3
                WHEN 'waiting_on_customer' THEN 4
                WHEN 'resolved' THEN 5
                WHEN 'closed' THEN 6
            END
    """)).fetchall()

    # --- Override breakdown by field ---
    # Shows per-field accuracy: how often each AI field gets overridden
    override_rows = db.execute(text("""
        SELECT
            f.field,
            COALESCE(o.override_count, 0) AS override_count,
            (SELECT COUNT(*) FROM ai_enrichments) AS total_enriched,
            CASE
                WHEN (SELECT COUNT(*) FROM ai_enrichments) = 0 THEN 0
                ELSE ROUND(
                    1.0 - (COALESCE(o.override_count, 0)::numeric
                    / (SELECT COUNT(*) FROM ai_enrichments)), 3
                )
            END AS accuracy_rate
        FROM (
            VALUES ('severity'), ('category'), ('suggested_response')
        ) AS f(field)
        LEFT JOIN (
            SELECT override_field, COUNT(*) AS override_count
            FROM agent_actions
            WHERE action_type = 'override'
            GROUP BY override_field
        ) o ON f.field = o.override_field
        ORDER BY f.field
    """)).fetchall()

    return DashboardCharts(
        by_severity=[
            TicketByField(label=r.label, count=r.count) for r in severity_rows
        ],
        by_category=[
            TicketByField(label=r.label, count=r.count) for r in category_rows
        ],
        by_status=[
            TicketByField(label=r.label, count=r.count) for r in status_rows
        ],
        override_breakdown=[
            OverrideBreakdown(
                field=r.field,
                override_count=r.override_count,
                total_enriched=r.total_enriched,
                accuracy_rate=float(r.accuracy_rate),
            )
            for r in override_rows
        ],
    )


# Why raw SQL here?
# The override breakdown query uses a VALUES clause to list all possible
# override fields, LEFT JOINs to the actual overrides, and calculates
# accuracy rates with CASE expressions. This is significantly cleaner
# in SQL than chaining ORM methods. In an interview, you can walk through
# this query and explain each part — that's the SQL fluency the Cognizant
# Data Engineer role is looking for.