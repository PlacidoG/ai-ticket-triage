
"""Tests for ticket CRUD endpoints."""


def test_health_check(test_client):
    """Health endpoint returns ok."""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_ticket(test_client):
    """POST /api/tickets returns 201 with correct fields."""
    response = test_client.post(
        "/api/tickets",
        json={
            "title": "Pytest: create ticket",
            "description": "Testing ticket creation via pytest.",
            "submitter_email": "pytest@company.com",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Pytest: create ticket"
    assert data["status"] == "new"
    assert data["source"] == "web_form"
    assert data["submitter_email"] == "pytest@company.com"
    assert "id" in data


def test_create_ticket_missing_title(test_client):
    """POST /api/tickets rejects empty title."""
    response = test_client.post(
        "/api/tickets",
        json={"title": "", "description": "Has a description"},
    )
    assert response.status_code == 422


def test_list_tickets(test_client, sample_ticket):
    """GET /api/tickets returns a paginated list."""
    response = test_client.get("/api/tickets")
    assert response.status_code == 200
    data = response.json()
    assert "tickets" in data
    assert "has_more" in data
    assert "next_cursor" in data
    assert isinstance(data["tickets"], list)


def test_list_tickets_with_limit(test_client, sample_ticket):
    """GET /api/tickets?limit=1 returns exactly 1 ticket."""
    response = test_client.get("/api/tickets?limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["tickets"]) <= 1


def test_get_ticket_detail(test_client, sample_ticket):
    """GET /api/tickets/{id} returns ticket with enrichment field."""
    ticket_id = sample_ticket["id"]
    response = test_client.get(f"/api/tickets/{ticket_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == ticket_id
    assert "enrichment" in data


def test_get_ticket_not_found(test_client):
    """GET /api/tickets/{bad_id} returns 404."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = test_client.get(f"/api/tickets/{fake_id}")
    assert response.status_code == 404


def test_update_ticket_status(test_client, sample_ticket):
    """PATCH /api/tickets/{id} updates status."""
    ticket_id = sample_ticket["id"]
    response = test_client.patch(
        f"/api/tickets/{ticket_id}",
        json={"status": "in_progress", "agent_id": "agent_pytest"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_update_ticket_invalid_status(test_client, sample_ticket):
    """PATCH /api/tickets/{id} rejects invalid status."""
    ticket_id = sample_ticket["id"]
    response = test_client.patch(
        f"/api/tickets/{ticket_id}",
        json={"status": "banana"},
    )
    assert response.status_code == 422


def test_intake_with_valid_key(test_client):
    """POST /api/intake with valid key returns 201."""
    response = test_client.post(
        "/api/intake",
        json={
            "title": "Pytest: intake ticket",
            "description": "Testing intake endpoint.",
            "source": "monitoring",
        },
        headers={"X-API-Key": "intake-dev-key-2026"},
    )
    assert response.status_code == 201
    assert response.json()["source"] == "monitoring"


def test_intake_with_bad_key(test_client):
    """POST /api/intake with bad key returns 401."""
    response = test_client.post(
        "/api/intake",
        json={
            "title": "Should fail",
            "description": "Bad key.",
        },
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 401


def test_dashboard_summary(test_client):
    """GET /api/dashboard/summary returns expected shape."""
    response = test_client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_tickets" in data
    assert "open_tickets" in data
    assert "ai_accuracy_rate" in data
    assert "total_enrichment_cost" in data


def test_dashboard_charts(test_client):
    """GET /api/dashboard/charts returns expected shape."""
    response = test_client.get("/api/dashboard/charts")
    assert response.status_code == 200
    data = response.json()
    assert "by_severity" in data
    assert "by_category" in data
    assert "by_status" in data
    assert "override_breakdown" in data