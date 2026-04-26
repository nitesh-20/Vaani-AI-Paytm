"""
parser.py — PhonePe CSV / raw text → list of structured dicts

Supports:
  - CSV files (primary, our default format)
  - Raw pasted PhonePe statement text
  - DD/MM/YYYY and YYYY-MM-DD date formats
  - ₹ symbol, commas in amounts
"""

import json
import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Union, List


# ─── Raw dict shape produced by parser ─────────────────────────────────────
# {
#   "date":    "2024-03-15",     str ISO date
#   "time":    "14:32:05",       str
#   "type":    "debit"|"credit", str lowercase
#   "amount":  500.0,            float
#   "name":    "Himanshu Verma", str (raw, not yet normalized)
#   "account": "HDFC ***1234",   str
# }
# ────────────────────────────────────────────────────────────────────────────


def _parse_amount(raw: str) -> float:
    """Strip ₹, commas, whitespace → float."""
    cleaned = re.sub(r"[₹,\s]", "", str(raw))
    return float(cleaned)


def _parse_date(raw: str) -> str:
    """Return ISO date string (YYYY-MM-DD) from various formats."""
    raw = raw.strip()
    if 'T' in raw:
        raw = raw.split('T')[0]
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError(f"Unrecognised date format: {raw!r}")


def _parse_time(raw: str) -> str:
    """Normalise time string to HH:MM:SS."""
    raw = raw.strip()
    if 'T' in raw:
        raw = raw.split('T')[1]
    for fmt in ("%H:%M:%S", "%H:%M", "%I:%M %p", "%I:%M:%S %p"):
        try:
            return datetime.strptime(raw, fmt).strftime("%H:%M:%S")
        except ValueError:
            continue
    return raw  # return as-is if unrecognised


def _normalise_type(raw: str) -> str:
    val = raw.strip().lower()
    if "credit" in val or "cr" == val:
        return "credit"
    if "debit" in val or "dr" == val:
        return "debit"
    # For merchant statements, SUCCESS usually means money received
    if "success" in val or "completed" in val:
        return "credit"
    return val


def _mask_account(raw: str) -> str:
    """Mask account numbers for privacy (e.g. 'XXXX1234')."""
    s = str(raw).strip()
    if not s:
        return ""
    # If already masked, keep it
    if "*" in s or "X" in s:
        return s
    # Only keep last 4 digits
    digits = re.sub(r'[^0-9]', '', s)
    if len(digits) >= 4:
        return f"XXXX{digits[-4:]}"
    return s


def parse_csv(path: Union[str, Path]) -> list[dict]:
    """
    Load transactions from a CSV file.

    Expected columns (case-insensitive):
        date, time, type, amount, name, account

    Returns list of normalised transaction dicts.
    """
    transactions = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # normalise header keys
        for row in reader:
            row = {k.strip().lower(): v.strip() for k, v in row.items()}
            try:
                txn = {
                    "date": _parse_date(row.get("date", "")),
                    "time": _parse_time(row.get("time", "00:00:00")),
                    "type": _normalise_type(row.get("type", "")),
                    "amount": _parse_amount(row.get("amount", "0")),
                    "name": row.get("name", "Unknown"),
                    "account": _mask_account(row.get("account", "")),
                }
                transactions.append(txn)
            except (ValueError, KeyError) as e:
                # skip malformed rows silently
                continue
    return transactions


# ─── Raw text parser (PhonePe statement copy-paste) ─────────────────────────

# Example raw text block:
#   Date: 15 Mar 2024
#   Time: 02:32 PM
#   Transaction Type: Debit
#   Amount: ₹500.00
#   To: Himanshu Verma
#   Account: HDFC Bank ***1234

_RAW_PATTERNS = {
    "date":    re.compile(r"Date[:\s]+(.+)", re.IGNORECASE),
    "time":    re.compile(r"Time[:\s]+(.+)", re.IGNORECASE),
    "type":    re.compile(r"(?:Transaction\s+)?Type[:\s]+(.+)", re.IGNORECASE),
    "amount":  re.compile(r"Amount[:\s]+(.+)", re.IGNORECASE),
    "name":    re.compile(r"(?:To|From|Name)[:\s]+(.+)", re.IGNORECASE),
    "account": re.compile(r"(?:Account|Bank)[:\s]+(.+)", re.IGNORECASE),
}

_RAW_DATE_FORMATS = [
    "%d %b %Y", "%d %B %Y", "%d/%m/%Y", "%Y-%m-%d",
    "%d-%m-%Y", "%B %d, %Y",
]


def _parse_raw_date(raw: str) -> str:
    raw = raw.strip()
    for fmt in _RAW_DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return raw


def parse_raw_text(text: str) -> list[dict]:
    """
    Parse one or more PhonePe-style copy-pasted statement blocks.

    Blocks are separated by blank lines or "---" dividers.
    """
    # split into blocks
    blocks = re.split(r"\n\s*\n|\n---+\n", text.strip())
    transactions = []

    for block in blocks:
        if not block.strip():
            continue
        txn = {}
        for field, pattern in _RAW_PATTERNS.items():
            m = pattern.search(block)
            if m:
                txn[field] = m.group(1).strip()

        if not txn:
            continue

        try:
            transactions.append({
                "date":    _parse_raw_date(txn.get("date", "")),
                "time":    _parse_time(txn.get("time", "00:00:00")),
                "type":    _normalise_type(txn.get("type", "")),
                "amount":  _parse_amount(txn.get("amount", "0")),
                "name":    txn.get("name", "Unknown"),
                "account": _mask_account(txn.get("account", "")),
            })
        except (ValueError, KeyError):
            continue

    return transactions


# ─── PhonePe PDF statement parser ───────────────────────────────────────────
#
# Format (copy-paste from PhonePe PDF):
#
#   Dec 20, 2025
#   02:24 PM
#   Paid to Swiggy Ltd
#   Transaction ID : AXBed40e...
#   UTR No : 572041427985
#   Debited from XX3905
#   Debit INR 1.00
#
# Edge cases handled:
#   - Date/time split across lines ("Feb 05,\n2026", "08:42\nPM")
#   - Amount split ("Credit INR\n25000.00")
#   - Masked names ("Paid to ******4837" → "Masked 4837")
#   - Self-transfers ("Paid to XXXXXXXX4010" → "Self Transfer")
#   - Mobile recharge, Payment Received, bare "Paid"
# ────────────────────────────────────────────────────────────────────────────

_MONTHS = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
)
_MONTHS_RE = "|".join(_MONTHS)

# Lines to discard from PhonePe PDF text
_JUNK_PATTERNS = [
    re.compile(r"^Page \d+ of \d+$"),
    re.compile(r"support\.phonepe\.com"),
    re.compile(r"^Date\s+Transaction Details\s+Type\s+Amount$", re.IGNORECASE),
    re.compile(r"This is a system generated", re.IGNORECASE),
    re.compile(r"^https?://"),
    re.compile(r"^For any queries"),
]


def _is_junk(line: str) -> bool:
    return any(p.search(line) for p in _JUNK_PATTERNS)


def _preprocess_phonepe_text(text: str) -> str:
    """
    Fix PDF text extraction artifacts in PhonePe statements:
      - Split dates:  "Dec 20,\n2025"  → "Dec 20, 2025"
      - Split times:  "08:42\nPM"      → "08:42 PM"
      - Split amounts: "INR\n25000.00" → "INR 25000.00"
      - Remove junk/header lines
    """
    lines = [l.strip() for l in text.split("\n")]
    out = []

    i = 0
    while i < len(lines):
        line = lines[i]
        if not line or _is_junk(line):
            i += 1
            continue

        # Fix split date: "Dec 20," followed by year on next line
        if re.match(rf"^({_MONTHS_RE})\s+\d{{1,2}},?$", line) and i + 1 < len(lines):
            nxt = lines[i + 1].strip()
            if re.match(r"^\d{4}$", nxt):
                line = f"{line.rstrip(',')} {nxt}"
                i += 2
                out.append(line)
                continue

        # Fix split time: "HH:MM" followed by "AM" or "PM" on next line
        if re.match(r"^\d{1,2}:\d{2}$", line) and i + 1 < len(lines):
            nxt = lines[i + 1].strip()
            if nxt in ("AM", "PM"):
                line = f"{line} {nxt}"
                i += 2
                out.append(line)
                continue

        # Fix split amount: "Credit INR" or "Debit INR" followed by number
        if re.match(r"^(Credit|Debit)\s+INR$", line, re.IGNORECASE) and i + 1 < len(lines):
            nxt = lines[i + 1].strip()
            if re.match(r"^[\d,]+\.?\d*$", nxt):
                line = f"{line} {nxt}"
                i += 2
                out.append(line)
                continue

        out.append(line)
        i += 1

    return "\n".join(out)


def _extract_name_from_description(desc: str) -> tuple[str, str]:
    """
    Parse description line → (name, type).
    Returns ("Swiggy Ltd", "debit") etc.
    """
    desc = desc.strip()

    # "Received from <name>"
    m = re.match(r"^Received from\s+(.+)$", desc, re.IGNORECASE)
    if m:
        return _clean_phonepe_name(m.group(1).strip()), "credit"

    # "Payment Received"
    if re.match(r"^Payment Received$", desc, re.IGNORECASE):
        return "Payment Received", "credit"

    # "Paid to <name>"
    m = re.match(r"^Paid to\s+(.+)$", desc, re.IGNORECASE)
    if m:
        return _clean_phonepe_name(m.group(1).strip()), "debit"

    # "Paid - <description>" (e.g. "Paid - Mobile Recharge")
    m = re.match(r"^Paid\s*[-–]\s*(.+)$", desc, re.IGNORECASE)
    if m:
        return m.group(1).strip(), "debit"

    # Bare "Paid"
    if re.match(r"^Paid$", desc, re.IGNORECASE):
        return "Unknown Payment", "debit"

    return desc, "unknown"


def _clean_phonepe_name(raw: str) -> str:
    """Normalise masked or special names from PhonePe."""
    raw = raw.strip()

    # Fully masked: "XXXXXXXX4010" or "XXXXXX3905"
    if re.match(r"^[Xx*]{4,}(\d{3,4})$", raw):
        digits = re.sub(r"[Xx*]", "", raw)
        return f"Self Transfer (XX{digits})"

    # Partially masked: "******4837" or "******0691"
    if re.match(r"^\*{4,}(\d{3,4})$", raw):
        digits = re.sub(r"\*", "", raw)
        return f"Masked (****{digits})"

    # Bank account: "Bank Account XXXXXXX2831"
    if re.match(r"^Bank Account", raw, re.IGNORECASE):
        return "Bank Transfer"

    # "Mr <name>", "Mrs <name>", "Ms <name>" — strip honorific
    m = re.match(r"^(?:Mr\.?\s+|Mrs\.?\s+|Ms\.?\s+|Dr\.?\s+)(.+)$", raw, re.IGNORECASE)
    if m:
        return m.group(1).strip()

    return raw


def parse_phonepe_statement_text(text: str) -> list[dict]:
    """
    Parse a PhonePe PDF statement pasted as plain text.

    Handles the exact format from PhonePe's PDF export.
    """
    # Step 1: Pre-process to fix PDF artifacts
    cleaned = _preprocess_phonepe_text(text)
    lines = [l for l in cleaned.split("\n") if l.strip()]

    transactions = []
    i = 0
    n = len(lines)

    # Patterns
    date_re = re.compile(rf"^({_MONTHS_RE})\s+\d{{1,2}},?\s*\d{{4}}$")
    time_re = re.compile(r"^\d{1,2}:\d{2}\s*(?:AM|PM)$", re.IGNORECASE)
    desc_re = re.compile(
        r"^(Paid to|Received from|Paid\s*[-–]|Payment Received|Paid)(\s+.+)?$",
        re.IGNORECASE
    )
    amount_re = re.compile(r"^(Credit|Debit)\s+INR\s+([\d,\s]+\.?\d*)$", re.IGNORECASE)
    account_re = re.compile(r"^(Debited from|Credited to)\s+(\S+)$", re.IGNORECASE)
    category_re = re.compile(r"^Category[:\s]+(.+)$", re.IGNORECASE)
    merchant_re = re.compile(r"^Merchant\s+ID[:\s]+(.+)$", re.IGNORECASE)

    while i < n:
        # Look for a date line
        if not date_re.match(lines[i]):
            i += 1
            continue

        # Found a date — start a new transaction
        date_str = lines[i].replace(",", "")
        date_parsed = ""
        for fmt in ("%b %d %Y", "%B %d %Y"):
            try:
                date_parsed = datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
                break
            except ValueError:
                continue

        if not date_parsed:
            i += 1
            continue

        i += 1

        # Time line
        time_parsed = "00:00:00"
        if i < n and time_re.match(lines[i]):
            try:
                time_parsed = datetime.strptime(
                    lines[i].strip().upper(), "%I:%M %p"
                ).strftime("%H:%M:%S")
            except ValueError:
                pass
            i += 1

        # Description line
        name = "Unknown"
        txn_type = "unknown"
        while i < n:
            m = desc_re.match(lines[i])
            if m:
                name, txn_type = _extract_name_from_description(lines[i])
                i += 1
                break
            # Skip non-description lines (unlikely between time and desc)
            if date_re.match(lines[i]):
                break  # next transaction started prematurely
            i += 1

        # Scan rest of block for account + amount + category + merchant
        account = ""
        amount = 0.0
        category = ""
        merchant_id = ""
        final_type = txn_type

        while i < n:
            line = lines[i]

            # Stop if we hit the next transaction's date
            if date_re.match(line):
                break

            # Category/Merchant lines
            cat_m = category_re.match(line)
            if cat_m:
                category = cat_m.group(1).strip().lower()
            
            mid_m = merchant_re.match(line)
            if mid_m:
                merchant_id = mid_m.group(1).strip()

            # Amount line (also confirms type)
            m = amount_re.match(line)
            if m:
                raw_amt = re.sub(r"[\s,]", "", m.group(2))
                try:
                    amount = float(raw_amt)
                except ValueError:
                    pass
                final_type = m.group(1).strip().lower()
                i += 1
                break  # amount is usually the last field

            # Account line
            m = account_re.match(line)
            if m:
                account = m.group(2).strip()

            i += 1

        # Only emit if we have a valid amount
        if amount > 0:
            transactions.append({
                "date":    date_parsed,
                "time":    time_parsed,
                "type":    final_type,
                "amount":  amount,
                "name":    name,
                "account": _mask_account(account),
                "category": category,
                "merchant_id": merchant_id,
            })

    return transactions


def load(source: Union[str, Path, List[Union[str, Path]]]) -> list[dict]:
    """
    Auto-detect source and parse.
    - list of sources -> recurses and combines
    - directory -> loads all valid files within
    - .csv  → parse_csv
    - .txt  → parse_phonepe_statement_text (PhonePe PDF format)
    - .json → load_json and normalise
    - multi-line string → parse_phonepe_statement_text
    """
    if isinstance(source, list):
        all_txns = []
        for s in source:
            all_txns.extend(load(s))
        return all_txns

    p = Path(source) if isinstance(source, str) else source
    
    if p.exists():
        if p.is_dir():
            all_txns = []
            # Sort for consistency
            for f in sorted(p.iterdir()):
                if f.suffix.lower() in ('.json', '.csv', '.txt'):
                    all_txns.extend(load(f))
            return all_txns
            
        if p.is_file():
            suffix = p.suffix.lower()
            if suffix == ".csv":
                return parse_csv(p)
            if suffix == ".json":
                with open(p, 'r') as f:
                    data = json.load(f)
                # Support both list of txns or object with 'transactions' key
                raw_txns = data if isinstance(data, list) else data.get("transactions", [])
                
                # Normalise fields to match parser's output format
                norm_txns = []
                for r in raw_txns:
                    try:
                        # Map common field names
                        d = {
                            "date":    _parse_date(r.get("date", r.get("timestamp", ""))),
                            "time":    _parse_time(r.get("time", r.get("timestamp", "00:00:00"))),
                            "type":    _normalise_type(r.get("type", r.get("status", ""))),
                            "amount":  float(r.get("amount", 0)),
                            "name":    r.get("name", r.get("counterparty", r.get("recipient", "Unknown"))),
                            "account": _mask_account(r.get("account", "")),
                            "category": r.get("category", ""),
                        }
                        norm_txns.append(d)
                    except Exception:
                        continue
                return norm_txns
            if suffix == ".txt":
                return parse_phonepe_statement_text(p.read_text(encoding="utf-8"))
            # fallback
            return parse_raw_text(p.read_text(encoding="utf-8"))
            
    # treat as raw text blob
    return parse_phonepe_statement_text(str(source))
 
 
 
 
 
 
