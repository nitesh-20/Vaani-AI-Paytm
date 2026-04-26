"""
intent_engine.py — Map raw user speech → (intent, params) using regex rules.

Handles Hindi/Hinglish + English.

Returns:
  {"intent": "<function_name>", "params": {...}}
  or
  {"intent": "unknown", "params": {}, "message": "<fallback>"}
"""

import re
from datetime import date, timedelta
from typing import Optional


# ─── Language detection ───────────────────────────────────────────────────────

_HINDI_MARKERS = {
    "kitna", "aaya", "gaya", "kya", "hai", "tha", "aaj", "kal", "karo",
    "bata", "kahan", "zyada", "pe", "mein", "unse", "unka", "haan",
    "nahi", "bheja", "kharch", "paisa", "diya", "liya", "pichla",
    "kaun", "sabse", "kuch", "koi", "mujhe", "tumhe", "dekho", "batao",
    "yaar", "bhai", "woh", "yeh", "lag", "lagta",
}


def detect_lang(text: str) -> str:
    """Return 'hi' if Hinglish/Hindi words detected, else 'en'."""
    words = set(text.lower().split())
    return "hi" if words & _HINDI_MARKERS else "en"


# ─── Date extraction ──────────────────────────────────────────────────────────

def _extract_date(text: str):
    """
    Extract a date reference from user text.
    Returns:
      "today", "yesterday", ("YYYY-MM-DD", "YYYY-MM-DD") for ranges, or None.
    """
    t = text.lower()
    if re.search(r"\baaj\b|\btoday\b|\babhi\b", t):
        return "today"
    if re.search(r"\bkal\b|\byesterday\b", t):
        return "yesterday"
    if re.search(r"\bis (hafte|week)\b|this week\b", t):
        start = date.today() - timedelta(days=date.today().weekday())
        end = date.today()
        return (str(start), str(end))
    if re.search(r"\bpichle? (hafte|week)\b|last week\b", t):
        today = date.today()
        end = today - timedelta(days=today.weekday() + 1)
        start = end - timedelta(days=6)
        return (str(start), str(end))
    if re.search(r"\bis mahine?\b|this month\b", t):
        today = date.today()
        start = today.replace(day=1)
        return (str(start), str(today))
    if re.search(r"\bpichle? mahine?\b|last month\b", t):
        today = date.today()
        first_this_month = today.replace(day=1)
        last_month_end = first_this_month - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        return (str(last_month_start), str(last_month_end))
    return None


def _extract_amount(text: str) -> Optional[float]:
    """Extract a numeric amount from text. Handles '500', '1,200', '1500 rupees'."""
    m = re.search(r"(\d[\d,]*(?:\.\d+)?)\s*(?:rupees?|rs\.?|₹)?", text)
    if m:
        return float(m.group(1).replace(",", ""))
    return None


_SKIP_WORDS = {
    "kitna", "kya", "kab", "kaise", "how", "much", "when", "what",
    "last", "recent", "pichla", "aaj", "today", "kal", "yesterday",
    "total", "transaction", "payment", "paisa", "paise", "money",
    "mere", "mera", "meri", "koi", "kuch", "wala", "wali",
}


def _extract_name(text: str) -> Optional[str]:
    """
    Extract a person name from query patterns like:
      'himanshu ne kitna', 'rahul ka transaction', 'from priya', 'to neha'

    Captures 1-2 words before/after the particle — avoids greedy over-capture.
    """
    # Pattern 1: <name (1-2 words)> ne/ka/ki/ke/se ...
    m = re.search(
        r"(?:^|\s)([A-Za-z]{2,}(?:\s[A-Za-z]{2,})?)\s+(?:ne|ka|ki|ke|se|ko)\b",
        text, re.IGNORECASE
    )
    if m:
        candidate = m.group(1).strip()
        if candidate.lower() not in _SKIP_WORDS:
            return candidate

    # Pattern 2: from/to/by <name>
    m = re.search(r"(?:from|to|by)\s+([A-Za-z]{2,}(?:\s[A-Za-z]{2,})?)", text, re.IGNORECASE)
    if m:
        candidate = m.group(1).strip()
        if candidate.lower() not in _SKIP_WORDS:
            return candidate

    # Pattern 3: <name> sent/bheja/diya — only take word immediately before verb
    m = re.search(
        r"([A-Za-z]{2,}(?:\s[A-Za-z]{2,})?)\s+(?:sent|paid|transferred|bheja|diya)\b",
        text, re.IGNORECASE
    )
    if m:
        # take only last 1-2 words of the match to avoid over-capture
        words = m.group(1).strip().split()
        candidate = words[-1] if len(words) == 1 else f"{words[-2]} {words[-1]}"
        if candidate.lower() not in _SKIP_WORDS:
            return candidate

    return None


def _extract_category(text: str) -> Optional[str]:
    """Extract category keyword from text."""
    t = text.lower()
    category_keywords = {
        "food":          ["food", "khana", "khaana", "restaurant", "swiggy", "zomato", "pizza", "burger"],
        "transport":     ["transport", "uber", "ola", "cab", "taxi", "metro", "travel", "rapido", "fuel", "petrol"],
        "recharge":      ["recharge", "jio", "airtel", "mobile", "dth"],
        "loan":          ["loan", "emi", "finance", "lending", "mpokket"],
        "entertainment": ["entertainment", "movie", "netflix", "bookmyshow", "hotstar"],
        "shopping":      ["shopping", "amazon", "flipkart", "myntra", "mart", "kirana", "store"],
        "education":     ["education", "school", "college", "university", "institute", "tuition", "fees"],
        "health":        ["health", "medical", "medicine", "pharmacy", "hospital", "gym", "fitness"],
        "person":        ["person", "log", "friends", "family"],
    }
    for cat, keywords in category_keywords.items():
        for kw in keywords:
            if kw in t:
                return cat
    return None


# ─── Intent patterns ──────────────────────────────────────────────────────────
# Each entry: (regex, intent_name, priority)
# Higher priority number = checked first

_INTENT_PATTERNS = [
    # WhatsApp report — highest priority so "send report on whatsapp" doesn't hit person patterns
    (r"(send|bhejo|share).*(whatsapp|wp).*(report|summary)", "send_whatsapp_report", 11),
    (r"(whatsapp|wp).*(pe|par|pe bhejo|report|summary)", "send_whatsapp_report", 11),
    (r"(weekly|is hafte|this week).*(report|summary).*(whatsapp|wp|send|bhejo)", "send_whatsapp_report", 11),
    (r"(whatsapp|wp).*(weekly|this week|report)", "send_whatsapp_report", 11),
    (r"send.*(report|summary).*(whatsapp|wp)", "send_whatsapp_report", 11),

    # Last transaction
    (r"(last|pichla|pichli|recent|latest|abhi wala|latest wala)\s+(transaction|payment|transfer|wala)", "get_last_transaction", 10),
    (r"(last|pichla|pichli)\s+(kya|kya tha|kya hai)", "get_last_transaction", 10),
    (r"last transaction", "get_last_transaction", 10),
    (r"pichla transaction", "get_last_transaction", 10),

    # Check specific payment
    (r"\b(\d[\d,]*)\s*(aaya|mila|received|credit|aa gaya|kya aaya|aaya kya)", "check_payment", 9),
    (r"(kya|did|check)\s+(\d[\d,]*)\s*(aaya|came|received|credit)", "check_payment", 9),

    # Total received
    (r"(kitna|how much|total)\s+(paisa\s+)?(aaya|receiv|mila|credit|income|aa gaya)", "get_total_received", 8),
    (r"(paisa|paise|money|amount)\s+(aaya|receiv|mila|credit)", "get_total_received", 8),
    (r"(receiv|income|credit)\s+(kitna|how much|total)", "get_total_received", 8),
    (r"(how much|total).*(receiv|came in|got paid)", "get_total_received", 8),
    (r"(did i|have i).*(receiv|get paid|earn)", "get_total_received", 8),

    # Total spent / debited
    (r"(kitna|how much|total)\s+(paisa\s+)?(gaya|spent|kharch|debit|nikla|gaya kya)", "get_total_spent", 8),
    (r"(kharch|spend|spent|debit|nikla)\s+(kitna|how much|total|hua|kiya)", "get_total_spent", 8),
    (r"(kitna|how much)\s+(kharch (hua|kiya))", "get_total_spent", 8),
    (r"(how much|total).*(spend|spent|paid out|went out)", "get_total_spent", 8),
    (r"(did i|have i).*(spend|pay|spent)", "get_total_spent", 8),

    # Top category — check BEFORE generic "zyada kharch" patterns
    (r"(kahan|where|kahin)\s+(zyada|most|max)\s*(kharch|spent|spend|gaya)", "get_top_category", 10),
    (r"(top|main|biggest)\s+(category|kharch|expense)", "get_top_category", 10),
    (r"kahan zyada|sabse zyada kharch|most spending", "get_top_category", 10),

    # Top person
    (r"(kaun|who)\s+(sabse zyada|most|max)\s+(bheja|send|sent|credit|diya)", "get_top_person", 10),
    (r"(top|most)\s+(person|sender|payer)", "get_top_person", 10),

    # Category spend — specific category + spend keyword → higher priority than generic totals
    (r"(food|khana|transport|recharge|loan|emi|entertainment|shopping|education|health|fees|medical)\s+(pe|par|mein)?\s*(kitna|how much|spend|kharch|gaya)", "get_category_spend", 9),
    (r"(kitna|how much)\s+(food|khana|transport|recharge|loan|entertainment|shopping|education|health)\b", "get_category_spend", 9),
    (r"(spend|spent|spending).*(on|for)\s+(food|transport|recharge|loan|entertainment|shopping|education|health)", "get_category_spend", 9),
    (r"(how much).*(on|for)\s+(food|transport|recharge|loan|entertainment|shopping|education|health)", "get_category_spend", 9),

    # Anomalies / insights
    (r"(unusual|suspicious|strange|anomal)", "detect_anomalies", 8),
    (r"(koi bada|kuch alag|kuch strange)", "detect_anomalies", 8),

    # Spending trend
    (r"(trend|pattern|breakdown|weekly|monthly|daily)", "get_spending_trend", 7),
    (r"(kab zyada|kab kam|spending pattern)", "get_spending_trend", 7),

    # Person query — broad, keep lower priority
    (r"(\w+)\s+(ne kitna|ne kya|ka transaction|ki payment|ke transactions)", "get_transactions_by_person", 5),
    (r"(from|to|by)\s+(\w+)", "get_transactions_by_person", 5),
    (r"(\w+)\s+(sent|paid|bheja|diya|transferred)", "get_transactions_by_person", 5),
    (r"(\w+)\s+(ka|ki|ke)\s+(paisa|paise|payment|transaction)", "get_transactions_by_person", 5),
]

# Sort by priority descending so highest-priority patterns are tested first
_INTENT_PATTERNS.sort(key=lambda x: x[2], reverse=True)

_FALLBACK_MESSAGE = (
    "I can answer questions about your transactions. "
    "Try asking: how much did I receive today, last transaction, "
    "food spending, or about a specific person like 'Himanshu ne kitna bheja'."
)


# ─── Main parse function ──────────────────────────────────────────────────────

def parse_intent(text: str) -> dict:
    """
    Parse user text into intent + params.

    Returns:
      {
        "intent":   str,
        "params":   dict,
        "raw_text": str,
      }
    """
    t = text.lower().strip()

    lang = detect_lang(text)

    for pattern, intent, _priority in _INTENT_PATTERNS:
        if re.search(pattern, t, re.IGNORECASE):
            params = _build_params(intent, text)
            return {"intent": intent, "params": params, "raw_text": text, "lang": lang}

    return {
        "intent": "unknown",
        "params": {},
        "raw_text": text,
        "lang": lang,
        "message": _FALLBACK_MESSAGE,
    }


def _build_params(intent: str, text: str) -> dict:
    """Extract relevant params for the matched intent."""
    params: dict = {}

    if intent in ("get_total_received", "get_total_spent"):
        d = _extract_date(text)
        params["date"] = d if isinstance(d, str) else None
        params["date_range"] = d if isinstance(d, tuple) else None

    elif intent == "check_payment":
        params["amount"] = _extract_amount(text)
        d = _extract_date(text)
        params["date"] = d if isinstance(d, str) else None

    elif intent == "get_transactions_by_person":
        params["name"] = _extract_name(text)

    elif intent == "get_category_spend":
        params["category"] = _extract_category(text)
        d = _extract_date(text)
        params["date_range"] = d if isinstance(d, tuple) else None

    elif intent == "get_spending_trend":
        d = _extract_date(text)
        params["date_range"] = d if isinstance(d, tuple) else None

    elif intent == "get_top_person":
        # detect if asking about receiver (debit); default to sender (credit)
        t = text.lower()
        if re.search(r"diya|paid|kharch|receiver|received by", t):
            params["type"] = "debit"
        else:
            params["type"] = "credit"

    elif intent == "send_whatsapp_report":
        t = text.lower()
        if re.search(r"last week|pichle hafte|pichla hafte", t):
            params["period"] = "last_week"
        elif re.search(r"this month|is mahine", t):
            params["period"] = "this_month"
        else:
            params["period"] = "this_week"  # default

    return params
 
 
 
 
 
 
 
 
 
