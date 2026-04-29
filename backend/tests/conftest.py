
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.models.base import Base

# Use the same database but wrap tests in transactions
# that roll back — so tests don't pollute real data
TEST_DATABASE_URL = "postgresql://Mr.shady_user:passwordisshady@localhost:5432/ai_ticket_triage"
engine = create_engine(TEST_DATABASE_URL)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture
def test_client():
    return client


@pytest.fixture
def db_session():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_ticket(test_client):
    """Create a ticket for tests that need an existing ticket."""
    response = test_client.post(
        "/api/tickets",
        json={
            "title": "Test ticket for pytest",
            "description": "This is a test ticket created by the test suite.",
            "submitter_email": "test@company.com",
        },
    )
    assert response.status_code == 201
    return response.json()