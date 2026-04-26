"""
query_engine.py — In-memory query layer over normalised+categorised transactions.

All operations are deterministic and sub-millisecond.

Public API:
  QueryEngine(path)             — load CSV from path
  .get_total_received(date)
  .get_total_spent(date)
  .get_transactions_by_person(name)
  .get_last_transaction()
  .check_payment(amount, date)
  .get_category_spend(category, date_range)
  .startup_summary()
"""

import os
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional, Union

from .parser import load as parse_file
from .normalizer import normalise, find_canonical_name
from .categorizer import categorise_all
from . import insight_engine as _ie


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _fmt_amount(amount: float) -> str:
    """TTS-safe amount: 'Rs 1,234' (no ₹ symbol — breaks Deepgram TTS)."""
    return f"Rs {amount:,.0f}"


def _resolve_date(date_input) -> Optional[date]:
    """
    Accept:
      - None            → None (means "all time")
      - "today"         → date.today()
      - "yesterday"     → date.today() - 1 day
      - "this_week"     → None (handled by date_range)
      - datetime.date   → as-is
      - "YYYY-MM-DD"    → parsed
    """
    if date_input is None:
        return None
    if isinstance(date_input, date):
        return date_input
    if isinstance(date_input, str):
        s = date_input.lower().strip()
        if s == "today":
            return date.today()
        if s in ("yesterday", "kal"):
            return date.today() - timedelta(days=1)
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def _filter_by_date(txns: list[dict], date_filter) -> list[dict]:
    if date_filter is None:
        return txns
    return [t for t in txns if t["date"] == date_filter]


def _filter_by_range(txns: list[dict], start: date, end: date) -> list[dict]:
    return [t for t in txns if start <= t["date"] <= end]


# ─── QueryEngine ─────────────────────────────────────────────────────────────

class QueryEngine:
    def __init__(self, path: Union[str, Path, None] = None):
        """
        Load and prepare transactions from CSV.
        path defaults to TRANSACTIONS_FILE env var or 'data/transactions.csv'.
        """
        if path is None:
            path = os.getenv(
                "TRANSACTIONS_FILE",
                Path(__file__).parent.parent / "data"
            )
        raw = parse_file(path)
        normalised = normalise(raw)
        self.transactions: list[dict] = categorise_all(normalised)

        # sort by date + time ascending (most recent last)
        self.transactions.sort(key=lambda t: (t["date"], t["time"]))

    # ── Core queries ──────────────────────────────────────────────────────────

    def get_total_received(self, date_input=None) -> dict:
        """Total credits on a given date (or all time if None)."""
        d = _resolve_date(date_input)
        pool = _filter_by_date(self.transactions, d) if d else self.transactions
        credits = [t for t in pool if t["type"] == "credit"]
        total = sum(t["amount"] for t in credits)
        return {
            "total": total,
            "count": len(credits),
            "date": str(d) if d else "all time",
            "transactions": credits,
        }

    def get_total_spent(self, date_input=None) -> dict:
        """Total debits on a given date (or all time if None)."""
        d = _resolve_date(date_input)
        pool = _filter_by_date(self.transactions, d) if d else self.transactions
        debits = [t for t in pool if t["type"] == "debit"]
        total = sum(t["amount"] for t in debits)
        return {
            "total": total,
            "count": len(debits),
            "date": str(d) if d else "all time",
            "transactions": debits,
        }

    def get_transactions_by_person(self, name: str) -> dict:
        """
        Find all transactions involving a person (fuzzy name match).
        Returns both sent and received.
        """
        canonical = find_canonical_name(name, self.transactions)
        if not canonical:
            return {
                "found": False,
                "query": name,
                "canonical": None,
                "transactions": [],
                "total_sent": 0.0,
                "total_received": 0.0,
            }

        txns = [t for t in self.transactions if t["name"] == canonical]
        sent = sum(t["amount"] for t in txns if t["type"] == "debit")
        received = sum(t["amount"] for t in txns if t["type"] == "credit")

        return {
            "found": True,
            "query": name,
            "canonical": canonical,
            "transactions": txns,
            "total_sent": sent,
            "total_received": received,
            "count": len(txns),
        }

    def get_last_transaction(self) -> dict:
        """Return the most recent transaction."""
        if not self.transactions:
            return {"found": False}
        last = self.transactions[-1]
        return {"found": True, "transaction": last}

    def check_payment(self, amount: float, date_input=None) -> dict:
        """
        Check if a payment of given amount was received (credit) on a date.
        Tolerance: ±5% of amount for fuzzy match.
        """
        d = _resolve_date(date_input)
        pool = _filter_by_date(self.transactions, d) if d else self.transactions

        tolerance = amount * 0.05
        exact = [t for t in pool if abs(t["amount"] - amount) < 0.01]
        fuzzy = [t for t in pool if abs(t["amount"] - amount) <= tolerance and t not in exact]

        if exact:
            return {"found": True, "exact": True, "amount": amount, "matches": exact}
        if fuzzy:
            return {"found": True, "exact": False, "amount": amount, "matches": fuzzy}

        # find closest
        all_credits = [t for t in self.transactions if t["type"] == "credit"]
        if all_credits:
            closest = min(all_credits, key=lambda t: abs(t["amount"] - amount))
            return {
                "found": False,
                "amount": amount,
                "closest": closest,
            }
        return {"found": False, "amount": amount, "closest": None}

    def get_category_spend(
        self,
        category: str,
        date_range: Optional[tuple] = None,
    ) -> dict:
        """
        Total spend in a category.
        date_range: (start_date, end_date) as date objects or ISO strings.
        """
        cat = category.lower().strip()
        if date_range:
            start = _resolve_date(date_range[0]) or date(2000, 1, 1)
            end = _resolve_date(date_range[1]) or date.today()
            pool = _filter_by_range(self.transactions, start, end)
        else:
            pool = self.transactions

        matching = [t for t in pool if t.get("category") == cat and t["type"] == "debit"]
        total = sum(t["amount"] for t in matching)
        return {
            "category": cat,
            "total": total,
            "count": len(matching),
            "transactions": matching,
        }

    # ── Startup summary ───────────────────────────────────────────────────────

    def startup_summary(self) -> str:
        """
        Returns an impactful financial greeting with today's snapshot,
        top category, most active person, anomaly count, and peak spend hour.
        """
        user_name = os.environ.get("USER_NAME", "")
        greeting_name = f" {user_name}" if user_name else ""

        today_received = self.get_total_received("today")
        today_spent = self.get_total_spent("today")
        has_today = today_received["total"] > 0 or today_spent["total"] > 0

        lines: list[str] = [f"Hey{greeting_name}! I'm Orion, your finance assistant."]

        # ── Money in / out ────────────────────────────────────────────────────
        if has_today:
            rec = _fmt_amount(today_received["total"])
            spnt = _fmt_amount(today_spent["total"])
            if today_received["total"] > 0 and today_spent["total"] > 0:
                lines.append(f"Today: received {rec}, spent {spnt}.")
            elif today_received["total"] > 0:
                lines.append(f"Today: received {rec}.")
            else:
                lines.append(f"Today: spent {spnt}.")
        else:
            total_r = self.get_total_received()
            total_s = self.get_total_spent()
            lines.append(
                f"Overall: received {_fmt_amount(total_r['total'])}, "
                f"spent {_fmt_amount(total_s['total'])}."
            )

        # ── Top spending category (excluding self-transfers) ──────────────────
        cat_totals: dict[str, float] = defaultdict(float)
        for t in self.transactions:
            if t["type"] == "debit" and t.get("category") not in ("self",):
                cat_totals[t.get("category", "other")] += t["amount"]
        _CAT_LABELS = {
            "person": "people", "other": "miscellaneous", "loan": "loans",
        }
        if cat_totals:
            top_cat = max(cat_totals, key=cat_totals.get)  # type: ignore[arg-type]
            top_cat_label = _CAT_LABELS.get(top_cat, top_cat)
            lines.append(f"Top category is {top_cat_label}, at {_fmt_amount(cat_totals[top_cat])} total.")

        # ── Most active sender ────────────────────────────────────────────────
        top_person_data = _ie.get_top_person(self.transactions, txn_type="credit")
        if top_person_data.get("found"):
            name = top_person_data["name"]
            first = str(name).split()[0]
            lines.append(f"Most active: {first} has sent you the most.")

        # ── Anomaly count ─────────────────────────────────────────────────────
        anomalies = _ie.detect_anomalies(self.transactions)
        if anomalies:
            lines.append(f"{len(anomalies)} unusually high transactions detected.")

        # ── Peak spending window ──────────────────────────────────────────────
        peak = _ie.get_peak_spending_hour(self.transactions)
        if peak.get("found"):
            lines.append(f"You spend most between {peak['label']}.")

        lines.append("What do you want to know?")
        return " ".join(lines)
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
