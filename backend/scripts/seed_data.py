
"""
Seed the database with 100 realistic tickets + real Claude enrichment.

Run from backend/:
    python -m scripts.seed_data

Clears all existing data before seeding.
Takes ~5 minutes due to Claude API calls.
"""

import random
import time
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import text

from app.database import SessionLocal
from app.models.ticket import Ticket
from app.models.ai_enrichment import AIEnrichment
from app.models.agent_action import AgentAction
from app.models.enums import TicketStatus, Severity, Category, TicketSource
from app.services.ai_service import enrich_ticket

# --- Config ---
TOTAL_TICKETS = 100
OVERRIDE_RATE = 0.20  # 20% of tickets get agent overrides
AGENTS = ["agent_alice", "agent_bob", "agent_carlos"]
MANAGER = "manager_carol"
SOURCES = ["web_form", "web_form", "web_form", "api", "monitoring", "email"]
# Weighted: 50% web_form, ~17% each for api/monitoring/email

# --- Ticket Templates ---
# Each has title, description, and expected category for override logic.
# Descriptions use {name} and {detail} placeholders for variation.

EMPLOYEES = [
    "Alice", "Bob", "Carlos", "Diana", "Erik", "Fatima", "Greg",
    "Hannah", "Ivan", "Julia", "Kevin", "Lisa", "Marcus", "Nina",
    "Oscar", "Priya", "Quinn", "Rosa", "Sam", "Tina", "Victor", "Wendy",
]

TICKET_TEMPLATES = [
    # === ACCOUNT ACCESS (clear-cut) ===
    {
        "title": "Can't log into my account",
        "description": "I've been locked out of my account since {time}. I've tried resetting my password but the reset email never arrives. I have {urgency}.",
        "category": "account_access",
    },
    {
        "title": "Password reset not working",
        "description": "I clicked 'Forgot Password' and entered my email {email} but haven't received the reset link. Checked spam folder too. Need access for {urgency}.",
        "category": "account_access",
    },
    {
        "title": "Account locked after too many attempts",
        "description": "My account got locked after I tried different passwords. Error message says 'Account temporarily disabled.' I need to {task}.",
        "category": "account_access",
    },
    {
        "title": "MFA token not working",
        "description": "My authenticator app shows a code but the system keeps rejecting it. I've tried multiple times. Getting 'Invalid verification code' error.",
        "category": "account_access",
    },
    {
        "title": "New employee needs system access",
        "description": "{name} started today in the {dept} department and needs access to {system}. Their manager is {manager}. Start date was today.",
        "category": "account_access",
    },
    {
        "title": "Can't access shared drive after password change",
        "description": "I changed my password yesterday and now I can't access the {dept} shared drive. Getting 'Access Denied' errors. Other systems work fine.",
        "category": "account_access",
    },

    # === BUG REPORT (clear-cut) ===
    {
        "title": "Export button gives 500 error",
        "description": "When I click 'Export to CSV' on the {page} page, I get a server error. Started happening after {event}. I can still view data in the browser.",
        "category": "bug_report",
    },
    {
        "title": "Application crashes when uploading large files",
        "description": "Every time I try to upload a file larger than 10MB to {system}, the application freezes and then crashes. Smaller files work fine.",
        "category": "bug_report",
    },
    {
        "title": "Dashboard shows wrong numbers",
        "description": "The {page} dashboard is showing {metric} as $0 when it should be around ${amount}. Other departments have confirmed the same issue.",
        "category": "bug_report",
    },
    {
        "title": "Search function returning no results",
        "description": "The search bar on {system} returns 'No results found' for everything, even terms I know exist. This started {time}.",
        "category": "bug_report",
    },
    {
        "title": "Page loads extremely slowly",
        "description": "The {page} page takes over 30 seconds to load. Other pages are fine. This started after {event}. Multiple users on my team are affected.",
        "category": "bug_report",
    },
    {
        "title": "Form submission silently fails",
        "description": "When I submit the {page} form, it shows a spinner for about 10 seconds, then nothing happens. No error message, no confirmation. Data doesn't save.",
        "category": "bug_report",
    },
    {
        "title": "Print function outputs garbled text",
        "description": "Printing from {system} produces pages of garbled characters instead of the actual document content. Screen display looks normal.",
        "category": "bug_report",
    },

    # === BILLING (clear-cut) ===
    {
        "title": "Charged twice for monthly subscription",
        "description": "I was billed ${amount} twice on {date} for my monthly subscription. Transaction IDs: {txn1} and {txn2}. Need a refund for the duplicate.",
        "category": "billing",
    },
    {
        "title": "Invoice doesn't match agreed pricing",
        "description": "Our latest invoice shows ${amount}/month but our contract says ${lower_amount}/month. Account ID: {acct}. Can someone review?",
        "category": "billing",
    },
    {
        "title": "Need to update payment method",
        "description": "Our company credit card on file expired. I need to update it to our new card ending in {card}. Please don't let the account lapse.",
        "category": "billing",
    },
    {
        "title": "Unexpected charge on department budget",
        "description": "There's a ${amount} charge from {date} on the {dept} department budget that nobody recognizes. Can you identify what this was for?",
        "category": "billing",
    },

    # === FEATURE REQUEST (clear-cut) ===
    {
        "title": "Add dark mode to the dashboard",
        "description": "The bright white background is hard on the eyes during {shift} shifts. A dark mode toggle in settings would be really helpful for our team.",
        "category": "feature_request",
    },
    {
        "title": "Need bulk export for reports",
        "description": "Currently I can only export reports one at a time. I need to export {count} reports monthly for {dept}. A bulk export feature would save hours.",
        "category": "feature_request",
    },
    {
        "title": "Calendar integration request",
        "description": "It would be great if {system} could sync with our Google Calendar. Right now I manually copy meeting links and it's error-prone.",
        "category": "feature_request",
    },
    {
        "title": "Mobile app request",
        "description": "Our field team needs to access {system} from their phones. The web version isn't usable on mobile. A native app or responsive redesign would help.",
        "category": "feature_request",
    },
    {
        "title": "Keyboard shortcuts for common actions",
        "description": "I process {count} tickets daily and having keyboard shortcuts for status changes and assignment would significantly speed up my workflow.",
        "category": "feature_request",
    },

    # === GENERAL (clear-cut) ===
    {
        "title": "How do I change my notification settings?",
        "description": "I'm getting too many email notifications from {system}. Where do I find the settings to reduce them? I only want alerts for {preference}.",
        "category": "general",
    },
    {
        "title": "Training request for new system",
        "description": "Our team is switching to {system} next month and we need training. There are {count} people on the team. Can someone arrange a session?",
        "category": "general",
    },
    {
        "title": "Need a copy of our service agreement",
        "description": "Legal is asking for a copy of our current service agreement with {vendor}. I can't find it in our shared drive. Can you send it over?",
        "category": "general",
    },
    {
        "title": "Conference room display not connecting",
        "description": "The display in conference room {room} won't connect to laptops. We've tried HDMI and wireless. We have a client meeting there {time}.",
        "category": "general",
    },

    # === AMBIGUOUS / EDGE CASES ===
    {
        "title": "System is completely unusable",
        "description": "Nothing works. Every page I click gives an error. I can't do my job. This has been going on since {time} and my entire team is affected.",
        "category": "bug_report",  # AI might say general
    },
    {
        "title": "Marriage last name change update",
        "description": "I recently got married and changed my last name from {old_name} to {new_name}. I need to update my work email, badge, and all system profiles.",
        "category": "account_access",  # AI often says general
    },
    {
        "title": "Laptop battery dies within an hour",
        "description": "My company laptop ({model}) won't hold a charge for more than an hour. It's {age} years old. Can I get a replacement or repair?",
        "category": "general",  # Could be bug_report
    },
    {
        "title": "Can someone explain our PTO policy?",
        "description": "I'm confused about how PTO accrual works after {years} years. The employee handbook says one thing but HR told me something different.",
        "category": "general",  # Not really IT but realistic
    },
    {
        "title": "Suspicious email received",
        "description": "I got an email from '{sender}' asking me to click a link to verify my account. It looks suspicious but I'm not sure. I haven't clicked anything.",
        "category": "general",  # Could be account_access (security)
    },
    {
        "title": "Software license expired mid-project",
        "description": "My {software} license expired today and I'm in the middle of a critical {dept} deliverable due {time}. I can't open my files.",
        "category": "billing",  # Could be bug_report or account_access
    },
    {
        "title": "Requesting temporary contractor access",
        "description": "We have a contractor named {name} starting a {duration} engagement with {dept}. They need limited access to {system} and email.",
        "category": "account_access",  # Could be general
    },
    {
        "title": "WiFi keeps dropping in building B",
        "description": "The WiFi on the {floor} floor of building B drops every 15-20 minutes. It reconnects after a minute but it's disrupting video calls.",
        "category": "bug_report",  # Could be general (infrastructure)
    },
    {
        "title": "Need to revoke access for terminated employee",
        "description": "{name} in {dept} was terminated today. Please immediately revoke all system access, email, badge access, and VPN credentials.",
        "category": "account_access",
    },
    {
        "title": "My monitor keeps flickering",
        "description": "The external monitor at my desk keeps flickering every few seconds. It's giving me headaches. I've tried different cables. Model: {model}.",
        "category": "general",  # Hardware issue, ambiguous category
    },
    {
        "title": "Data looks corrupted in report",
        "description": "The {dept} quarterly report is showing negative numbers for revenue which is impossible. The raw data in {system} looks correct. Something is wrong with the calculation.",
        "category": "bug_report",
    },
    {
        "title": "Can we get standing desks?",
        "description": "Several people on the {dept} team have been asking about standing desks. Is there a budget for ergonomic equipment? About {count} people interested.",
        "category": "general",  # Not IT at all
    },
]

# --- Randomization helpers ---

URGENCY = [
    "a client meeting in 30 minutes",
    "a deadline at end of day",
    "a presentation tomorrow morning",
    "a quarterly review this week",
    "no specific deadline but it's blocking my work",
]
TIMES = ["this morning", "yesterday afternoon", "last Friday", "about an hour ago", "since Monday"]
DEPTS = ["Engineering", "Sales", "Marketing", "Finance", "HR", "Operations", "Legal", "Support"]
SYSTEMS = ["Salesforce", "Jira", "Confluence", "Workday", "SAP", "ServiceNow", "Slack", "Teams"]
PAGES = ["reports", "analytics", "user management", "inventory", "billing"]
EVENTS = ["yesterday's update", "the server migration last week", "the security patch on Friday"]
FLOORS = ["2nd", "3rd", "4th", "5th"]
SHIFTS = ["evening", "night", "early morning", "late"]
SOFTWARE = ["Adobe Creative Suite", "AutoCAD", "MATLAB", "Microsoft Office", "Tableau"]
MODELS = ["Dell XPS 15", "ThinkPad X1 Carbon", "MacBook Pro 14", "HP EliteBook", "Surface Pro"]


def fill_template(template: dict) -> dict:
    """Fill placeholders in title and description with random values."""
    name = random.choice(EMPLOYEES)
    replacements = {
        "name": name,
        "email": f"{name.lower()}@company.com",
        "time": random.choice(TIMES),
        "urgency": random.choice(URGENCY),
        "dept": random.choice(DEPTS),
        "system": random.choice(SYSTEMS),
        "page": random.choice(PAGES),
        "event": random.choice(EVENTS),
        "manager": random.choice(EMPLOYEES),
        "floor": random.choice(FLOORS),
        "shift": random.choice(SHIFTS),
        "software": random.choice(SOFTWARE),
        "model": random.choice(MODELS),
        "task": f"submit the {random.choice(DEPTS)} report by end of day",
        "metric": random.choice(["revenue", "headcount", "expenses", "pipeline"]),
        "amount": str(random.randint(49, 999)),
        "lower_amount": str(random.randint(20, 48)),
        "count": str(random.randint(5, 50)),
        "date": f"March {random.randint(1, 28)}",
        "txn1": f"TXN-{random.randint(100000, 999999)}",
        "txn2": f"TXN-{random.randint(100000, 999999)}",
        "acct": f"ACCT-{random.randint(1000, 9999)}",
        "card": str(random.randint(1000, 9999)),
        "preference": random.choice(["critical issues", "my tickets only", "weekly digest"]),
        "vendor": random.choice(["Microsoft", "AWS", "Salesforce", "Oracle", "Zoom"]),
        "room": random.choice(["A", "B", "C", "D"]) + str(random.randint(101, 410)),
        "old_name": random.choice(["Smith", "Johnson", "Garcia", "Brown"]),
        "new_name": random.choice(["Nakamura", "O'Brien", "Worthington", "Chen-Williams"]),
        "age": str(random.randint(2, 5)),
        "years": str(random.randint(1, 8)),
        "sender": random.choice(["it-security@company-verify.com", "admin@acc0unt-reset.net", "noreply@update-required.org"]),
        "duration": random.choice(["3-month", "6-month", "2-week", "1-year"]),
    }

    title = template["title"]
    desc = template["description"]
    for key, val in replacements.items():
        title = title.replace(f"{{{key}}}", val)
        desc = desc.replace(f"{{{key}}}", val)

    return {
        "title": title,
        "description": desc,
        "expected_category": template["category"],
    }


def random_past_datetime(days_back: int = 14) -> datetime:
    """Return a random datetime within the last N days."""
    now = datetime.now(timezone.utc)
    seconds_back = random.randint(60, days_back * 24 * 3600)
    return now - timedelta(seconds=seconds_back)


def maybe_override(db, ticket, enrichment, agents) -> None:
    """With OVERRIDE_RATE probability, simulate an agent override."""
    if random.random() > OVERRIDE_RATE:
        return

    agent = random.choice(agents)
    field = random.choice(["severity", "category"])

    old_value = getattr(enrichment, field)

    if field == "severity":
        options = [s.value for s in Severity if s.value != old_value]
    else:
        options = [c.value for c in Category if c.value != old_value]

    new_value = random.choice(options)
    setattr(enrichment, field, new_value)

    action = AgentAction(
        ticket_id=ticket.id,
        agent_id=agent,
        action_type="override",
        override_field=field,
        old_value=old_value,
        new_value=new_value,
    )
    db.add(action)


def progress_ticket(db, ticket, enrichment, agents) -> None:
    """Randomly advance some tickets through the status lifecycle."""
    roll = random.random()

    if roll < 0.15:
        # Stay as triaged (15%)
        return
    elif roll < 0.45:
        # Move to in_progress (30%)
        new_status = TicketStatus.IN_PROGRESS.value
    elif roll < 0.55:
        # Move to waiting_on_customer (10%)
        new_status = TicketStatus.WAITING_ON_CUSTOMER.value
    elif roll < 0.85:
        # Move to resolved (30%)
        new_status = TicketStatus.RESOLVED.value
    else:
        # Move to closed (15%)
        new_status = TicketStatus.CLOSED.value

    old_status = ticket.status
    ticket.status = new_status

    # Assign to an agent if moving to in_progress
    if new_status == TicketStatus.IN_PROGRESS.value and not ticket.assigned_to:
        ticket.assigned_to = random.choice(agents)

    # Log the status change
    action = AgentAction(
        ticket_id=ticket.id,
        agent_id=ticket.assigned_to or random.choice(agents),
        action_type="status_change",
        override_field="status",
        old_value=old_status,
        new_value=new_status,
    )
    db.add(action)


def main():
    db = SessionLocal()

    try:
        # --- Reset database ---
        print("Clearing existing data...")
        db.execute(text("DELETE FROM agent_actions"))
        db.execute(text("DELETE FROM ai_enrichments"))
        db.execute(text("DELETE FROM tickets"))
        db.commit()
        print("Database cleared.\n")

        # --- Generate tickets ---
        print(f"Generating {TOTAL_TICKETS} tickets with real Claude enrichment...")
        print("This will take ~5 minutes. Each dot is one ticket.\n")

        successful = 0
        failed = 0
        total_cost = 0.0
        start_time = time.time()

        for i in range(TOTAL_TICKETS):
            template = random.choice(TICKET_TEMPLATES)
            filled = fill_template(template)
            source = random.choice(SOURCES)
            created_at = random_past_datetime()

            # Create ticket
            ticket = Ticket(
                title=filled["title"],
                description=filled["description"],
                source=source,
                submitter_email=f"{random.choice(EMPLOYEES).lower()}@company.com",
                created_at=created_at,
                updated_at=created_at,
            )
            db.add(ticket)
            db.flush()  # get the ticket ID without committing

            # Enrich with Claude
            try:
                result = enrich_ticket(ticket.title, ticket.description)

                enrichment = AIEnrichment(
                    ticket_id=ticket.id,
                    severity=result["severity"],
                    category=result["category"],
                    summary=result["summary"],
                    suggested_response=result["suggested_response"],
                    confidence=result["confidence"],
                    model_used=result["model_used"],
                    prompt_version=result["prompt_version"],
                    tokens_in=result["tokens_in"],
                    tokens_out=result["tokens_out"],
                    estimated_cost=result["estimated_cost"],
                    raw_response=result["raw_response"],
                    created_at=created_at,
                    updated_at=created_at,
                )
                db.add(enrichment)

                ticket.status = TicketStatus.TRIAGED.value

                # Maybe override and progress
                maybe_override(db, ticket, enrichment, AGENTS)
                progress_ticket(db, ticket, enrichment, AGENTS)

                total_cost += result["estimated_cost"]
                successful += 1
                print(".", end="", flush=True)

            except Exception as e:
                # If enrichment fails, ticket stays as 'new'
                failed += 1
                print("x", end="", flush=True)

            # Small delay to avoid rate limits
            time.sleep(0.5)

            # Commit every 10 tickets
            if (i + 1) % 10 == 0:
                db.commit()
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                remaining = (TOTAL_TICKETS - i - 1) / rate
                print(f" [{i + 1}/{TOTAL_TICKETS}] "
                      f"~{remaining:.0f}s remaining, "
                      f"${total_cost:.4f} spent")

        # Final commit
        db.commit()

        elapsed = time.time() - start_time
        print(f"\n\n{'=' * 60}")
        print(f"SEED COMPLETE")
        print(f"{'=' * 60}")
        print(f"Tickets created:  {successful + failed}")
        print(f"Enriched:         {successful}")
        print(f"Failed:           {failed}")
        print(f"Total cost:       ${total_cost:.4f}")
        print(f"Avg cost/ticket:  ${total_cost / max(successful, 1):.4f}")
        print(f"Time elapsed:     {elapsed:.0f}s")
        print(f"{'=' * 60}")

    except Exception as e:
        db.rollback()
        print(f"\n\nSeed failed: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()