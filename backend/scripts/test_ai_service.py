
"""
Quick test script for the AI service.
Run from backend/: python -m scripts.ai-test_service
"""

from app.services.ai_service import enrich_ticket

TEST_TICKETS = [
    {
        "title": "Can't log into my account",
        "description": (
            "I've been locked out since this morning. I have a client "
            "presentation in 10 minutes and I can't access any of my files. "
            "Password reset isn't sending emails."
        ),
        "expected_severity": "critical",
        "expected_category": "account_access",
    },
    {
        "title": "Export button gives 500 error",
        "description": (
            "When I click 'Export to CSV' on the reports page, I get a "
            "server error. Started happening after yesterday's update. "
            "I can still view reports in the browser but can't download them."
        ),
        "expected_severity": "high",
        "expected_category": "bug_report",
    },
    {
        "title": "Can you add dark mode?",
        "description": (
            "Would be great to have a dark mode option for my work. "
            "The bright white background is hard on the eyes during "
            "late night shifts."
        ),
        "expected_severity": "low",
        "expected_category": "feature_request",
    },
    {
        "title": "Charged twice for subscription",
        "description": (
            "I was billed $49.99 twice this past March 15th for the same "
            "monthly subscription. I need a refund for the duplicate "
            "charge please. Order ID: ORD-2026-8834."
        ),
        "expected_severity": "high",
        "expected_category": "billing",
    },

    {
        "title": "Marriage last name change update request.",
        "description": (
            "Hi, I recently got married and changed my last name"
            "from Smith to Zunkerberger and need to update my "
            "work email and badge information."
        ),
        "expected_severity": "low",
        "expected_category": "account_access",
    },

]


def main():
    print("=" * 60)
    print("AI ENRICHMENT SERVICE TEST")
    print("=" *60)

    for i, test in enumerate(TEST_TICKETS, 1):
        print(f"\n--- Test {i}: {test['title']} ---")
        print(f"Expected: {test['expected_severity']} / {test['expected_category']}")

        try:
            result = enrich_ticket(test["title"], test["description"])

            sev_match = "✓" if result["severity"] == test["expected_severity"] else "✗"
            cat_match = "✓" if result["category"] == test["expected_category"] else "✗"

            print(f"Got:      {result['severity']} {sev_match} / {result['category']} {cat_match}")
            print(f"Confidence: {result['confidence']:.0%}")
            print(f"Summary: {result['summary']}")
            print(f"Tokens: {result['tokens_in']} in / {result['tokens_out']} out")
            print(f"Cost: ${result['estimated_cost']:.6f}")
            print(f"Model: {result['model_used']} (prompt {result['prompt_version']})")

        except Exception as e:
            print(f"FAILED: {e}")

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()