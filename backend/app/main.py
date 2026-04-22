
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import tickets, intake

# Show enrichment logs in terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(
    title="AI Ticket Triage Assistant",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(tickets.router)
app.include_router(intake.router)



@app.get("/health")
async def health_check():
    return {"status": "ok"}