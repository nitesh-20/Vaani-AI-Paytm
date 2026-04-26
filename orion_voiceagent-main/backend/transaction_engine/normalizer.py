"""
normalizer.py — Clean and standardise a parsed transaction list.

Operations:
  - Names → Title Case
  - Fuzzy-dedup names using difflib (>85% similarity → canonical form)
  - Dates → datetime.date objects
  - Amounts → float (already done by parser, enforced here)
  - Type → "credit" | "debit" (already done by parser, enforced here)
"""

from datetime import date, datetime
from difflib import SequenceMatcher
from typing import Optional


# ─── Name normalisation ──────────────────────────────────────────────────────

def normalise_name(name: str) -> str:
    """
    Title-case a name. Handles all-caps and all-lower.
    'HIMANSHU VERMA' → 'Himanshu Verma'
    'swiggy' → 'Swiggy'
    """
    return " ".join(w.capitalize() for w in name.strip().split())


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def build_name_map(names: list[str], threshold: float = 0.85) -> dict[str, str]:
    """
    Given a list of raw names, return a mapping {raw_name: canonical_name}.

    Canonical = the first seen representative that is most common.
    Names with >threshold similarity are merged under the same canonical.

    Example:
        ["HIMANSHU VERMA", "Himanshu Verma", "himanshu verma"]
        → all map to "Himanshu Verma"
    """
    canonical_map: dict[str, str] = {}
    seen_canonical: list[str] = []  # list of canonical names already chosen

    for raw in names:
        norm = normalise_name(raw)
        # check if norm is close to an existing canonical
        matched = None
        for canon in seen_canonical:
            if _similarity(norm, canon) >= threshold:
                matched = canon
                break
        if matched is None:
            seen_canonical.append(norm)
            matched = norm
        canonical_map[raw] = matched

    return canonical_map


# ─── Date normalisation ──────────────────────────────────────────────────────

def normalise_date(date_str: str) -> date:
    """ISO string '2024-03-15' → datetime.date(2024, 3, 15)."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


# ─── Full dataset normalisation ──────────────────────────────────────────────

def normalise(transactions: list[dict]) -> list[dict]:
    """
    Run the full normalisation pipeline on a parsed transaction list.
    Mutates and returns the list (copies each dict).
    """
    if not transactions:
        return []

    # Build name map over all unique raw names
    raw_names = [t["name"] for t in transactions]
    name_map = build_name_map(raw_names)

    normalised = []
    for t in transactions:
        n = dict(t)  # shallow copy
        n["name"] = name_map.get(t["name"], normalise_name(t["name"]))
        n["date"] = normalise_date(t["date"]) if isinstance(t["date"], str) else t["date"]
        n["amount"] = float(t["amount"])
        n["type"] = t["type"].lower().strip() if isinstance(t["type"], str) else t["type"]
        normalised.append(n)

    return normalised


def find_canonical_name(query: str, transactions: list[dict], threshold: float = 0.60) -> Optional[str]:
    """
    Given a user query fragment like 'himanshu', find the best matching
    canonical name in the dataset.

    Lower threshold (0.60) because users speak partial names.
    Returns None if no match above threshold.
    """
    query_norm = normalise_name(query)
    unique_names = list({t["name"] for t in transactions})

    best_name = None
    best_score = 0.0
    for name in unique_names:
        score = _similarity(query_norm, name)
        # also check partial containment (e.g. "Himanshu" in "Himanshu Verma")
        if query_norm.lower() in name.lower():
            score = max(score, 0.75)
        if score > best_score:
            best_score = score
            best_name = name

    return best_name if best_score >= threshold else None
 
 
 
 
 
 
 
 
 
 
