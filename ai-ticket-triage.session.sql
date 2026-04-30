-- Ticket distribution by status
SELECT status, COUNT(*) FROM tickets GROUP BY status ORDER BY count DESC;

-- Enrichment distribution by severity
SELECT severity, COUNT(*) FROM ai_enrichments GROUP BY severity;

-- Agent actions
SELECT action_type, COUNT(*) FROM agent_actions GROUP BY action_type;

-- Cost summary
SELECT
    COUNT(*) as total,
    ROUND(SUM(estimated_cost)::numeric, 4) as total_cost,
    ROUND(AVG(estimated_cost)::numeric, 4) as avg_cost
FROM ai_enrichments;




# 4/29/2026

SELECT t.id, t.title, t.status, e.severity, e.category, e.confidence
FROM tickets t
LEFT JOIN ai_enrichments e ON t.id = e.ticket_id
ORDER BY t.created_at DESC
LIMIT 5;