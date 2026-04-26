"""
categorizer.py — Assign category to a transaction based on keyword rules.

Categories: food | transport | recharge | loan | person | other

Logic:
  - Check transaction name (lowercase) against keyword lists
  - First match wins
  - If no keyword matches → check if name looks like a human name → "person"
  - Default fallback → "other"
"""

import re

CATEGORY_RULES: dict[str, list[str]] = {
    "self": [
        "self transfer",
    ],
    "loan": [
        "mpokket", "financial services",
        "emi", "loan", "bajaj", "hdfc loan", "icici loan",
        "axis loan", "sbi loan", "kotak loan", "poonawalla",
        "muthoot", "manappuram", "interest", "lending",
    ],
    "food": [
        "swiggy", "zomato", "uber eats", "ubereats",
        "restaurant", "hotel ", "food", "beverage", "juice", "juices",
        "cafe", "chai", "chay", "nasta", "nashta", "snack",
        "dhaba", "pizza", "burger", "mcdonald", "kfc", "domino",
        "biryani", "chaayos", "starbucks", "subway", "haldiram",
        "momos", "chinese", "darbar", "ganna", "gupchup", "mithai",
        "amruttulya", "soda burst", "blinkit", "zepto", "bigbasket",
        "grofers", "dunzo", "nature basket",
    ],
    "transport": [
        "uber", "ola", "rapido", "metro", "irctc", "redbus",
        "fuels", "filling station", "petrol", "fuel", "bmtc",
        "makemytrip", "goibibo", "indigo", "spicejet", "air india",
        "yatra", "cab", "taxi",
    ],
    "recharge": [
        "jio", "airtel", "vi ", " vi", "bsnl", "mtnl",
        "recharge", "dth", "tata sky", "dish tv", "sun direct",
        "d2h", "top up", "topup", "data pack",
    ],
    "shopping": [
        "amazon", "flipkart", "myntra", "nykaa", "ajio", "meesho",
        "snapdeal", "tatacliq", "reliance", "big bazaar",
        "mart", "supermart", "provision", "kirana", "store",
        "cloth", "westside", "d-mart", "dmart",
    ],
    "education": [
        "university", "institute", "college", "school", "academy",
        "tuition", "coaching",
    ],
    "entertainment": [
        "bookmyshow", "netflix", "amazon prime", "hotstar", "spotify",
        "youtube premium", "disney", "pvr", "inox", "cinepolis",
        "ticketgenie",
    ],
    "health": [
        "medical", "pharmacy", "chemist", "hospital", "clinic",
        "fitness", "gym", "befit",
    ],
}

# Pattern to detect human names: at least 2 words, each capitalised, no digits
_HUMAN_NAME_RE = re.compile(r"^[A-Z][a-z]+(?:\s[A-Z][a-z]+)+$")


def categorise(name: str) -> str:
    """
    Return the category string for a transaction name.
    name should already be title-cased (from normalizer).
    """
    name_lower = name.lower()

    for category, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if kw in name_lower:
                return category

    # Human name heuristic
    if _HUMAN_NAME_RE.match(name):
        return "person"

    return "other"


def categorise_all(transactions: list[dict]) -> list[dict]:
    """
    Add a 'category' field to each transaction dict.
    Returns new list (does not mutate originals).
    """
    result = []
    for t in transactions:
        n = dict(t)
        n["category"] = categorise(t.get("name", ""))
        result.append(n)
    return result
 
 
 
 
