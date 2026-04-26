"""
insight_engine.py — Detect trends, top persons, and anomalies from transaction data.

All functions operate on the normalised+categorised transaction list.
They are called by the query dispatcher for insight-type intents.
"""

from collections import defaultdict
from datetime import date, timedelta
from typing import Optional


def get_top_person(transactions: list[dict], txn_type: str = "credit") -> dict:
    """
    Return the person who sent you the most (type='credit')
    or received the most from you (type='debit').
    """
    totals: defaultdict[str, float] = defaultdict(float)
    counts: dict[str, int] = {}

    for t in transactions:
        if t["type"] == txn_type and t.get("category") == "person":
            totals[t["name"]] += t["amount"]
            counts[t["name"]] = counts.get(t["name"], 0) + 1

    if not totals:
        return {"found": False, "type": txn_type}

    top_name = max(totals, key=totals.__getitem__)
    return {
        "found": True,
        "name": top_name,
        "total": totals[top_name],
        "count": counts[top_name],
        "type": txn_type,
    }


def get_top_category(transactions: list[dict], date_range: Optional[tuple] = None) -> dict:
    """
    Return the category with the highest total debit spend.
    date_range: (start_date_str, end_date_str) or None for all time.
    """
    pool = transactions
    if date_range:
        try:
            from datetime import datetime
            start = datetime.strptime(str(date_range[0]), "%Y-%m-%d").date()
            end = datetime.strptime(str(date_range[1]), "%Y-%m-%d").date()
            pool = [t for t in transactions if start <= t["date"] <= end]
        except (ValueError, IndexError):
            pass

    totals: dict[str, float] = defaultdict(float)
    for t in pool:
        if t["type"] == "debit":
            cat = t.get("category", "other")
            if cat == "self":  # exclude internal transfers
                continue
            totals[cat] += t["amount"]

    if not totals:
        return {"found": False}

    grand_total = sum(totals.values())
    top_cat = max(totals, key=totals.__getitem__)
    top_total = totals[top_cat]
    pct = (top_total / grand_total * 100) if grand_total else 0

    return {
        "found": True,
        "category": top_cat,
        "total": top_total,
        "percentage": pct,
        "all_categories": dict(totals),
    }


def get_spending_trend(transactions: list[dict], days: int = 30) -> list[dict]:
    """
    Return day-by-day spend/receive summary for the last `days` days.
    """
    today = date.today()
    start = today - timedelta(days=days - 1)

    daily: dict[date, dict] = {}
    current = start
    while current <= today:
        daily[current] = {"date": str(current), "spent": 0.0, "received": 0.0}
        current += timedelta(days=1)

    for t in transactions:
        d = t["date"] if isinstance(t["date"], date) else date.fromisoformat(str(t["date"]))
        if d in daily:
            if t["type"] == "debit":
                daily[d]["spent"] += t["amount"]
            else:
                daily[d]["received"] += t["amount"]

    return list(daily.values())


def detect_anomalies(transactions: list[dict], multiplier: float = 2.5) -> list[dict]:
    """
    Flag transactions whose amount is >= multiplier × average debit amount.

    Returns list of {"transaction": dict, "reason": str, "ratio": float}.
    """
    debits = [t for t in transactions if t["type"] == "debit"]
    if len(debits) < 3:
        return []

    avg = sum(t["amount"] for t in debits) / len(debits)
    threshold = avg * multiplier

    anomalies = []
    for t in debits:
        if t["amount"] >= threshold:
            ratio = t["amount"] / avg
            anomalies.append({
                "transaction": t,
                "ratio": round(ratio, 1),
                "reason": f"{ratio:.1f}x your average spend of ₹{avg:,.0f}.",
            })

    # sort by ratio descending
    anomalies.sort(key=lambda x: x["ratio"], reverse=True)
    return anomalies


def get_peak_spending_hour(transactions: list[dict]) -> dict:
    """
    Find the 3-hour window with the highest debit spend.
    Returns: {"hour_start": 19, "hour_end": 22, "total": 12000, "count": 45}
    """
    ht: list[float] = [0.0] * 24  # totals per hour
    hc: list[int] = [0] * 24     # counts per hour

    for t in transactions:
        if t["type"] != "debit":
            continue
        raw_time = t.get("time", "")
        if not raw_time:
            continue
        try:
            hour = int(str(raw_time).split(":")[0])
            ht[hour] += float(t["amount"])
            hc[hour] += 1
        except (ValueError, IndexError):
            continue

    if not any(ht):
        return {"found": False}

    # Find best 3-hour window by total spend
    best_start: int = 0
    best_total: float = 0.0
    best_count: int = 0
    for h in range(24):
        window_total: float = 0.0
        window_count: int = 0
        for j in range(3):
            idx: int = (h + j) % 24
            window_total += ht[idx]
            window_count += hc[idx]
        if window_total > best_total:
            best_total = window_total
            best_start = h
            best_count = window_count

    end: int = (best_start + 3) % 24

    def _fmt_hour(h: int) -> str:
        suffix = "AM" if h < 12 else "PM"
        display = h if h <= 12 else h - 12
        if display == 0:
            display = 12
        return f"{display} {suffix}"

    return {
        "found": True,
        "hour_start": best_start,
        "hour_end": end,
        "label": f"{_fmt_hour(best_start)}–{_fmt_hour(end)}",
        "total": best_total,
        "count": best_count,
    }
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
