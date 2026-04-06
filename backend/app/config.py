import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://app_user:app_password@localhost:5432/ai_ticket_triage"
)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")