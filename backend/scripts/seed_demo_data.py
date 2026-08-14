"""Populate the ledger with a handful of demo claims so the dashboard
isn't empty on first run. Safe to run multiple times (duplicates get
deduped by the semantic-matching step, just bumping check_count).

Usage (from backend/):
    venv/Scripts/python.exe -m scripts.seed_demo_data
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Windows terminals often default to a legacy codepage (cp1252) that can't
# print rupee signs or emoji; force UTF-8 stdout so the script never crashes
# on its own console output.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.core.pipeline import run_verification_pipeline  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import InputType  # noqa: E402

DEMO_CLAIMS = [
    "Good morning everyone! Please forward to all your groups: 5G towers are spreading coronavirus in cities, stay safe, share with everyone!!",
    "Drinking cow urine daily cures COVID-19 completely.",
    "PM Kisan Yojana gives 6000 rupees per year to eligible farmer families.",
    "The RBI has banned the 2000 rupee note and it is now worthless paper.",
    "WhatsApp will start charging a monthly subscription fee from next month.",
    "Click this government link to register and get a free laptop for all students.",
    "NASA has confirmed six days of complete darkness next month due to planetary alignment.",
    "Government will give ₹50,000 to all engineering students this year.",
    "Eating garlic and turmeric completely prevents and cures cancer.",
    "The Ministry of Health has approved a new vaccination drive starting next quarter.",
]


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for text in DEMO_CLAIMS:
            try:
                result = run_verification_pipeline(db, text, InputType.TEXT)
                print(f"[{result.verdict}] {result.normalized_claim[:80]}")
            except Exception as exc:
                # One claim failing (rate limit, transient network error) shouldn't
                # abort the rest of the seed batch.
                db.rollback()
                print(f"[SKIPPED] {text[:80]} — {exc}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
