
from __future__ import annotations

import json
import logging
import time

import anthropic

from app.config import ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)

# --- Constants ---
MODEL = "claude-sonnet-4-20250514"
PROMPT_VERSION = "v1.0"
MAX_RETRIES = 3
BASE_DELAY = 1  #seconds

# Opus (swap in to compare — slower, smarter, more expensive)
# MODEL = "claude-opus-4-0-20250115""

# Pricing per million tokens (Sonnet 4)
# Check https://www.anthropic.com/pricing for current rates
COST_PER_M_INPUT = 3.00
COST_PER_M_OUTPUT = 15.00

SYSTEM_PROMPT = """You are an IT helpdesk ticket triage assistant. Your job is to analyze
incoming support tickets and return a structured classification.

## Categories (pick exactly one):
- bug_report: Software defects, errors, crashes, broken features
- billing: Payment issues, invoice questions, subscription problems
- account_access: Login failures, password resets, permission issues, lockouts
- feature_request: Enhancement suggestions, new functionality asks
- general: Questions, how-to requests, anything that doesn't fit above

## Severity scale (pick exactly one):
- critical: System down, data loss risk, security breach, blocks many users, urgent deadline
- high: Major feature broken, significant impact, workaround exists but painful
- medium: Minor feature issue, inconvenience, reasonable workaround available
- low: Cosmetic issue, nice-to-have, no urgency

## Confidence:
- Rate your confidence from 0.0 to 1.0 that your classification is correct
- Be honest — ambiguous tickets should get lower confidence (0.5-0.7)
- Clear-cut tickets should get high confidence (0.85-0.95)
- Almost nothing should be 1.0

## Output format:
Return ONLY valid JSON with no additional text, no markdown, no code fences:
{
    "severity": "critical|high|medium|low",
    "category": "bug_report|billing|account_access|feature_request|general",
    "summary": "1-2 sentence summary of the core issue",
    "suggested_response": "A helpful first reply to send the employee",
    "confidence": 0.85
}"""

# Initialize client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)



def enrich_ticket(title: str, description: str) -> dict:
    """Call Cluade to classify and enrich a support ticket.
    Returns a dict with: severity, category, summary, suggested_response,
    confidence, model_used, prompt_version, tokens_in, tokens_out,
    estimated_cost, raw_response.

    Retries up to 3 times with exponential backoff on failure.
    """
    user_message = f"Ticket title: {title}\n\nTicket description: {description}"

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                temperature=0,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": user_message}
                ],
            )

            # Extract text from response
            raw_text = response.content[0].text
            tokens_in = response.usage.input_tokens
            tokens_out = response.usage.output_tokens


            # Calculate cost
            estimated_cost = (
                (tokens_in / 1_000_000) * COST_PER_M_INPUT
                + (tokens_out / 1_000_000) * COST_PER_M_OUTPUT
                       
             )

            #Parse JSON from response
            enrichment = _parse_response(raw_text)

            # Validate fields
            enrichment = _validate_enrichment(enrichment)

            # Add metadata
            enrichment["model_used"] = MODEL
            enrichment["prompt_version"] = PROMPT_VERSION
            enrichment["tokens_in"] = tokens_in
            enrichment["tokens_out"] = tokens_out
            enrichment["estimated_cost"] = round(estimated_cost, 6)
            enrichment["raw_response"] = raw_text

            logger.info(
                "Enrichment succeeded on attempt %d — %s/%s (%.0f%% confidence)",
                attempt,
                enrichment["severity"],
                enrichment["category"],
                enrichment["confidence"] * 100,
            )

            return enrichment
        
        except json.JSONDecodeError as e:
            last_error = e
            logger.warning(
                "Attempt %d: Failed to parse JSON from Claude response: %s",
                attempt, str(e),
            )
        except anthropic.APIError as e:
            last_error = e
            logger.warning(
                "Attempt %d: Claude API error: %s", 
                attempt, str(e),
            )
        except Exception as e:
            last_error = e
            logger.warning(
                "Attempt %d: Unexpected error: %s",
                attempt, str(e),
            )

        # Exponential backoff: 1s, 2s, 4s
        if attempt < MAX_RETRIES:
            delay = BASE_DELAY * (2 ** (attempt - 1))
            logger.info("Retrying in %ds...", delay)
            time.sleep(delay)
    # All retries exhausted
    logger.error(
        "All %d enrichment attempts failed. Last error: %s",
        MAX_RETRIES, str(last_error),
    )
    raise RuntimeError(
        f"AI enrichment failed after {MAX_RETRIES} attempts: {last_error}"
    )


def _parse_response(raw_text: str) -> dict:
    """Parse JSON from Claude's response, handling common formatting issues."""
    text = raw_text.strip()

    # Strip markdown code fences if Claude includes them
    if text.startswith("```"):
        text = text.strip("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    return json.loads(text)


def _validate_enrichment(data: dict) -> dict:
    """Validate and normalize enrichment fields. Falls back to safe defaults."""
    valid_severities = {"critical", "high", "medium", "low"}
    valid_categories = {
        "bug_report", "billing", "account_access", 
        "feature_request", "general",
    }

    
    severity = data.get("severity", "medium").lower().strip()
    if severity not in valid_severities:
        logger.warning(
        "Invalid severity '%s', defaulting to 'medium'", severity)
        severity = "medium"
    

    category = data.get("category", "general").lower().strip()
    if category not in valid_categories:
        logger.warning(
            "Invalid category '%s', defaulting to 'general'", category)
        category = "general"

    confidence = data.get("confidence", 0.5)
    if not isinstance(confidence, (int, float)):
        confidence = 0.5
    confidence = max(0.0, min(1.0, float(confidence)))

    return {
        "severity": severity,
        "category": category,
        "summary": str(data.get("summary", "No summary available")),
        "suggested_response": str(data.get("suggested_response", "No response generated")),
        "confidence": round(confidence, 3),
    }

        