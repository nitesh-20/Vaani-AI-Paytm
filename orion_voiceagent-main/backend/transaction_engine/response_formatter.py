"""
response_formatter.py — Natural, conversational responses for Orion.

Supports two modes:
  lang="en"  — casual English, no robotic phrases
  lang="hi"  — Hinglish: Hindi fillers + English financial terms

Each function accepts an optional lang param. Default: "en".
"""

import os
from datetime import date, datetime
from typing import Optional


# ─── Shared helpers ───────────────────────────────────────────────────────────

def _fmt(amount: float) -> str:
    return f"₹{amount:,.0f}"


def _user() -> str:
    """First name from USER_NAME env var, or empty string."""
    name = os.environ.get("USER_NAME", "")
    return name.split()[0] if name else ""


def _fmt_time(raw_time: str) -> str:
    """HH:MM:SS → '2:30 PM'"""
    try:
        return datetime.strptime(raw_time, "%H:%M:%S").strftime("%-I:%M %p")
    except ValueError:
        return raw_time


def _date_label(d, lang: str = "en") -> str:
    """'today'/'aaj', 'yesterday'/'kal', 'March 15', etc."""
    if d is None:
        return "ab tak" if lang == "hi" else "overall"
    if isinstance(d, str):
        if d in ("today",):
            return "aaj" if lang == "hi" else "today"
        if d in ("yesterday",):
            return "kal" if lang == "hi" else "yesterday"
        if d in ("all time", "overall"):
            return "ab tak" if lang == "hi" else "overall"
        try:
            d = datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            return d
    if isinstance(d, date):
        today = date.today()
        if d == today:
            return "aaj" if lang == "hi" else "today"
        if (today - d).days == 1:
            return "kal" if lang == "hi" else "yesterday"
        return d.strftime("%B %d")
    return str(d)


def _short_name(name: str, max_words: int = 2) -> str:
    """First 1-2 meaningful words of a name, skipping single-letter initials."""
    import itertools
    words = [w for w in name.split() if len(w) > 1]
    return " ".join(itertools.islice(words, max_words)) if words else name.split()[0]


def _top_people(transactions: list, txn_type: str = "credit", n: int = 2) -> list:
    """Get top N names by total from a list of transactions."""
    import itertools
    totals: dict[str, float] = {}
    for t in transactions:
        if t.get("type") == txn_type:
            key = t.get("name", "?").split()[0]
            totals[key] = totals.get(key, 0.0) + float(t.get("amount", 0))
    ranked = sorted(totals.items(), key=lambda x: -x[1])
    return [{"name": k, "total": v} for k, v in itertools.islice(ranked, n)]


# ─── Formatters ───────────────────────────────────────────────────────────────

def format_total_received(data: dict, lang: str = "en") -> str:
    total = data.get("total", 0)
    count = data.get("count", 0)
    dl = _date_label(data.get("date"), lang)
    user = _user()

    if lang == "hi":
        if total == 0:
            addr = f"Haan {user} —" if user else "Haan —"
            return f"{addr} {dl} kuch nahi aaya. Inbox clear hai."
        addr = f"Haan {user} —" if user else "Haan —"
        base = f"{addr} {dl} {_fmt(total)} aaye hain"
        txns = data.get("transactions", [])
        senders = _top_people(txns, "credit")
        if senders and dl in ("aaj",):
            parts = ", ".join(f"{s['name']} {_fmt(s['total'])}" for s in senders)
            return f"{base}\n{parts}"
        return f"{base} — {count} payments mein."

    if total == 0:
        return f"Nothing came in {dl} — all clear."
    if count == 1:
        txns = data.get("transactions", [])
        if txns:
            return f"Received {_fmt(total)} {dl} — one payment from {txns[0]['name']}."
    return f"Received {_fmt(total)} {dl} across {count} payments."


def format_total_spent(data: dict, lang: str = "en") -> str:
    total = data.get("total", 0)
    count = data.get("count", 0)
    dl = _date_label(data.get("date"), lang)

    if lang == "hi":
        if total == 0:
            dl_cap = dl.capitalize()
            return f"{dl_cap} kuch kharch nahi hua. Paisa safe hai."
        return f"Dekho — {dl} {_fmt(total)} gaye hain\n{count} transactions mein."

    if total == 0:
        return f"Nothing spent {dl}. Balance untouched."
    if count == 1:
        txns = data.get("transactions", [])
        if txns:
            return f"Spent {_fmt(total)} {dl} — one payment to {txns[0]['name']}."
    return f"Spent {_fmt(total)} {dl} across {count} transactions."


def format_last_transaction(data: dict, lang: str = "en") -> str:
    if not data.get("found"):
        return "Koi transaction nahi mila abhi tak." if lang == "hi" else "No transaction data yet."

    t = data["transaction"]
    amount = _fmt(t["amount"])
    name = t.get("name", "?")
    first = name.split()[0]
    raw_time = t.get("time", "")
    time_str = _fmt_time(raw_time) if raw_time else ""
    dl = _date_label(t.get("date"), lang)

    if lang == "hi":
        direction = "se aaya" if t["type"] == "credit" else "ko gaya"
        base = f"Last transaction {amount} ka tha — {first} {direction}"
        when = dl + (f" around {time_str}" if time_str else "")
        return f"{base}\n{when}."

    direction = "from" if t["type"] == "credit" else "to"
    base = f"Last transaction: {amount} {direction} {name}"
    when = dl + (f" at {time_str}" if time_str else "")
    return f"{base} — {when}."


def format_person_query(data: dict, lang: str = "en") -> str:
    if not data.get("found"):
        name = data.get("query", "that person")
        if lang == "hi":
            return f"Yaar, {name} ke naam ka koi transaction nahi mila."
        return f"Couldn't find anyone named {name} in your transactions."

    canonical = data["canonical"]
    first = canonical.split()[0]
    count = data.get("count", 0)
    sent = data.get("total_sent", 0)
    received = data.get("total_received", 0)
    last_txn = data["transactions"][-1] if data.get("transactions") else None

    if lang == "hi":
        lines = []
        if received > 0 and sent > 0:
            lines.append(f"{first} se tumhara total:")
            lines.append(f"Aaya: {_fmt(received)} — Diya: {_fmt(sent)}")
            lines.append(f"Kul {count} transactions.")
        elif received > 0:
            lines.append(f"{first} ne tumhe {_fmt(received)} bheja hai — {count} baar")
            if last_txn:
                lines.append(f"Last: {_date_label(last_txn.get('date'), lang)}")
        else:
            lines.append(f"Tumne {first} ko {_fmt(sent)} diya hai — {count} baar")
        return "\n".join(lines)

    if sent > 0 and received > 0:
        return (
            f"With {canonical}: sent {_fmt(sent)}, received {_fmt(received)} "
            f"— {count} transaction{'s' if count != 1 else ''} total."
        )
    if received > 0:
        base = f"{canonical} sent you {_fmt(received)} across {count} payment{'s' if count != 1 else ''}."
        if last_txn:
            base += f" Last: {_date_label(last_txn.get('date'))}."
        return base
    if sent > 0:
        return f"Sent {_fmt(sent)} to {canonical} — {count} payment{'s' if count != 1 else ''}."
    return f"Found {canonical} in {count} transaction{'s' if count != 1 else ''} but amounts total zero."


def format_check_payment(data: dict, amount: float, lang: str = "en") -> str:
    if data.get("found"):
        matches = data.get("matches", [])
        if data.get("exact") and matches:
            t = matches[0]
            raw_time = t.get("time", "")
            time_str = _fmt_time(raw_time) if raw_time else ""
            dl = _date_label(t.get("date"), lang)
            first = t.get("name", "?").split()[0]
            if lang == "hi":
                direction = "se aaya" if t["type"] == "credit" else "ko gaya"
                when = dl + (f" around {time_str}" if time_str else "")
                return f"Haan — {_fmt(amount)} {first} {direction}\n{when}."
            direction = "came in from" if t["type"] == "credit" else "went out to"
            when = f" on {dl}" + (f" at {time_str}" if time_str else "")
            return f"Yes — {_fmt(amount)} {direction} {t['name']}{when}."
        if matches:
            t = matches[0]
            dl = _date_label(t.get("date"), lang)
            first = t.get("name", "?").split()[0]
            if lang == "hi":
                return f"Exact nahi mila, but close — {_fmt(t['amount'])} {first} ko gaya {dl}."
            return f"Close match — {_fmt(t['amount'])} {'from' if t['type'] == 'credit' else 'to'} {t['name']} on {dl}."

    closest = data.get("closest")
    if closest:
        dl = _date_label(closest.get("date"), lang)
        first = closest.get("name", "?").split()[0]
        if lang == "hi":
            return f"Nahi mila {_fmt(amount)} ka koi payment. Closest tha {_fmt(closest['amount'])} {first} ko, {dl}."
        return (
            f"No {_fmt(amount)} payment found. "
            f"Closest: {_fmt(closest['amount'])} {'from' if closest['type'] == 'credit' else 'to'} "
            f"{closest['name']} on {dl}."
        )
    if lang == "hi":
        return f"Records mein {_fmt(amount)} ka koi payment nahi mila."
    return f"No payment of {_fmt(amount)} found in your records."


def format_category_spend(data: dict, lang: str = "en") -> str:
    cat = data.get("category", "that category")
    total = data.get("total", 0)
    count = data.get("count", 0)

    _CAT_HI = {
        "food": "food", "transport": "transport", "recharge": "recharge",
        "loan": "loans", "shopping": "shopping", "education": "education",
        "health": "health", "entertainment": "entertainment",
        "person": "logon pe", "other": "misc",
    }

    if lang == "hi":
        cat_hi = _CAT_HI.get(cat, cat)
        if total == 0:
            return f"{cat_hi} pe abhi tak kuch nahi gaya."
        return f"Dekho — {cat_hi} pe around {_fmt(total)} gaya hai\n{count} transactions mein."

    if total == 0:
        return f"Nothing spent on {cat} yet."
    return f"Spent {_fmt(total)} on {cat} across {count} transaction{'s' if count != 1 else ''}."


def format_no_data(lang: str = "en") -> str:
    if lang == "hi":
        return "Abhi utna data nahi hai yeh batane ke liye."
    return "Not enough transaction data to answer that yet."


def format_unknown(message: Optional[str] = None, lang: str = "en") -> str:
    if message:
        return message
    if lang == "hi":
        return (
            "Yaar, yeh samajh nahi aaya. "
            "Pucho — kitna aaya, kitna gaya, ya kisi ke baare mein."
        )
    return (
        "I can answer questions about your transactions — "
        "received, spent, by person, by category, or the last one."
    )


def format_anomalies(data: list, lang: str = "en") -> str:
    if not data:
        if lang == "hi":
            return "Sab normal lag raha hai. Koi unusual transaction nahi mili."
        return "No unusual transactions found. Everything looks normal."

    import itertools
    count = len(data)

    if lang == "hi":
        if count == 1:
            item = data[0]
            t = item.get("transaction", {})
            ratio = item.get("ratio", 0)
            name = _short_name(t.get("name", "?"))
            direction = "se aaya" if t.get("type") == "credit" else "ko gaya"
            return (
                f"Ek cheez unusual lagi — {_fmt(t.get('amount', 0))} {name} {direction}\n"
                f"Normal se {ratio}x zyada hai. Tumhare pattern mein rare hai."
            )
        lines = []
        for item in itertools.islice(data, 3):
            t = item.get("transaction", {})
            ratio = item.get("ratio", 0)
            name = _short_name(t.get("name", "?"))
            direction = "se aaya" if t.get("type") == "credit" else "gaya"
            lines.append(f"• {_fmt(t.get('amount', 0))} {name} {direction} — {ratio}x zyada")
        summary = "\n".join(lines)
        extra = f"\n...aur {count - 3} aur bhi." if count > 3 else ""
        return (
            f"Haan, kuch unusual transactions hain 👇\n{summary}{extra}\n"
            f"Yeh tumhare normal pattern se match nahi karta."
        )

    if count == 1:
        item = data[0]
        t = item.get("transaction", {})
        ratio = item.get("ratio", 0)
        name = _short_name(t.get("name", "?"))
        direction = "from" if t.get("type") == "credit" else "sent to"
        return (
            f"⚠️ Something unusual: "
            f"{_fmt(t.get('amount', 0))} {direction} {name} — "
            f"{ratio}x your average. Doesn't match your normal pattern."
        )
    lines = []
    for item in itertools.islice(data, 3):
        t = item.get("transaction", {})
        ratio = item.get("ratio", 0)
        name = _short_name(t.get("name", "?"))
        direction = "from" if t.get("type") == "credit" else "to"
        lines.append(f"• {_fmt(t.get('amount', 0))} {direction} {name} — {ratio}x your average")
    summary = "\n".join(lines)
    extra = f"\n...and {count - 3} more." if count > 3 else ""
    return (
        f"⚠️ Found {count} unusual transactions:\n{summary}{extra}\n"
        f"These don't match your normal pattern."
    )


_CAT_LABELS = {
    "person": "people", "self": "self-transfers", "food": "food",
    "transport": "transport", "recharge": "recharge", "loan": "loans",
    "shopping": "shopping", "education": "education", "health": "health",
    "entertainment": "entertainment", "other": "miscellaneous",
}

_CAT_LABELS_HI = {
    "person": "logon pe", "self": "apne account mein",
    "food": "food pe", "transport": "transport pe",
    "recharge": "recharge pe", "loan": "loans pe",
    "shopping": "shopping pe", "education": "education pe",
    "health": "health pe", "entertainment": "entertainment pe",
    "other": "misc pe",
}


def format_top_category(data: dict, lang: str = "en") -> str:
    cat_key = data.get("category", "unknown")
    total = data.get("total", 0)
    pct = data.get("percentage", 0)
    if total == 0:
        return "Spending data nahi mila." if lang == "hi" else "No spending data found."
    if lang == "hi":
        cat = _CAT_LABELS_HI.get(cat_key, cat_key)
        pct_str = f" — tumhari spending ka {pct:.0f}%" if pct else ""
        return f"Sabse zyada kharch {cat} hua hai — {_fmt(total)} total{pct_str}."
    cat = _CAT_LABELS.get(cat_key, cat_key)
    pct_str = f" — {pct:.0f}% of your spending" if pct else ""
    return f"Top spending: {cat} — {_fmt(total)} total{pct_str}."


def format_top_person(data: dict, lang: str = "en") -> str:
    name = data.get("name", "unknown")
    first = name.split()[0]
    total = data.get("total", 0)
    count = data.get("count", 0)
    txn_type = data.get("type", "debit")
    if total == 0:
        return "Koi person data nahi mila." if lang == "hi" else "No person-to-person transaction data found."
    if lang == "hi":
        if txn_type == "credit":
            return f"{first} ne sabse zyada bheja hai — {_fmt(total)} total, {count} baar."
        return f"{first} ne sabse zyada liya hai — {_fmt(total)} total, {count} baar."
    direction = "sent you" if txn_type == "credit" else "received from you"
    return f"{name} {direction} the most — {_fmt(total)} across {count} transaction{'s' if count != 1 else ''}."


def format_spending_trend(data: list, lang: str = "en") -> str:
    if not data:
        return "Trend ke liye data nahi hai." if lang == "hi" else "Not enough data for a trend yet."
    total_spent = sum(d.get("spent", 0) for d in data)
    days = len(data)
    avg = total_spent / days if days else 0
    if lang == "hi":
        return (
            f"Pichle {days} dino mein {_fmt(total_spent)} kharch hua\n"
            f"Matlab roughly {_fmt(avg)} roz."
        )
    return f"Last {days} days: spent {_fmt(total_spent)} total — averaging {_fmt(avg)} per day."


def format_whatsapp_sent(success: bool, period: str, lang: str = "en") -> str:
    _labels_en = {"this_week": "This week's", "last_week": "Last week's", "this_month": "This month's"}
    _labels_hi = {"this_week": "is hafte ka", "last_week": "pichle hafte ka", "this_month": "is mahine ka"}
    if success:
        if lang == "hi":
            label = _labels_hi.get(period, "is hafte ka")
            return f"Done! {label} report tumhare WhatsApp pe bhej diya. Check karo!"
        label = _labels_en.get(period, "This week's")
        return f"Done! {label} report sent to your WhatsApp."
    if lang == "hi":
        return "Bhej nahi paya — Twilio settings check karo please."
    return "Couldn't send to WhatsApp — check your Twilio config in .env."

 
 
 
 
 
 
