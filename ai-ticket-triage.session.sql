
SELECT t.id, t.title, t.status, e.severity, e.category, confidence
FROM tickets t
JOIN ai_enrichments e ON t.id = e.ticket_id
LIMIT 5;

SELECT * FROM agent_actions ORDER BY created_at DESC;