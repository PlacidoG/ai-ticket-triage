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