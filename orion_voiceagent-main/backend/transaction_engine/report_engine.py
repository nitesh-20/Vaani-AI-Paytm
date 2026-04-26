"""
report_engine.py — Generate weekly/monthly financial reports.

Builds a summary dict from filtered transactions,
formats a WhatsApp-ready text message, and generates a PDF.
"""
import os
from datetime import date, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_report(transactions: list[dict], start: date, end: date) -> dict:
    """Filter transactions to date range and compute summary."""
    pool = [t for t in transactions if start <= t["date"] <= end]

    received = sum(t["amount"] for t in pool if t["type"] == "credit")
    spent = sum(
        t["amount"]
        for t in pool
        if t["type"] == "debit" and t.get("category") != "self"
    )

    # Top category
    cat_totals: dict[str, float] = {}
    for t in pool:
        if t["type"] == "debit" and t.get("category") not in ("self", None):
            cat = str(t["category"])
            cat_totals[cat] = cat_totals.get(cat, 0.0) + t["amount"]
    top_category = max(cat_totals, key=cat_totals.__getitem__) if cat_totals else None
    top_cat_amount = cat_totals.get(top_category, 0.0) if top_category else 0.0

    # Top sender (credit, person category)
    sender_totals: dict[str, float] = {}
    for t in pool:
        if t["type"] == "credit" and t.get("category") == "person":
            sender_totals[t["name"]] = sender_totals.get(t["name"], 0.0) + t["amount"]
    top_sender = max(sender_totals, key=sender_totals.__getitem__) if sender_totals else None
    top_sender_amount = sender_totals.get(top_sender, 0.0) if top_sender else 0.0

    # Day-by-day breakdown
    daily: list[dict] = []
    current = start
    while current <= end:
        ds = str(current)
        day_spent = sum(
            t["amount"]
            for t in pool
            if str(t["date"]) == ds and t["type"] == "debit" and t.get("category") != "self"
        )
        day_received = sum(
            t["amount"]
            for t in pool
            if str(t["date"]) == ds and t["type"] == "credit"
        )
        daily.append({"date": ds, "spent": day_spent, "received": day_received})
        current += timedelta(days=1)

    return {
        "start": str(start),
        "end": str(end),
        "transaction_count": len(pool),
        "received": received,
        "spent": spent,
        "net": received - spent,
        "top_category": top_category,
        "top_cat_amount": top_cat_amount,
        "top_sender": top_sender,
        "top_sender_amount": top_sender_amount,
        "daily": daily,
    }


def build_whatsapp_message(report: dict) -> str:
    """Format report dict into a WhatsApp-ready text string."""
    start = report["start"]
    end = report["end"]
    lines = [
        "📊 *Orion Weekly Report*",
        f"📅 {start} → {end}",
        "",
        f"💰 Received: ₹{report['received']:,.0f}",
        f"💸 Spent:    ₹{report['spent']:,.0f}",
        f"📈 Net:      ₹{report['net']:+,.0f}",
    ]
    if report["top_category"]:
        cat_label = str(report["top_category"]).title()
        lines.append(f"🏷️ Top category: {cat_label} (₹{report['top_cat_amount']:,.0f})")
    if report["top_sender"]:
        first = str(report["top_sender"]).split()[0]
        lines.append(f"👤 Top sender: {first} (₹{report['top_sender_amount']:,.0f})")
    lines.append("")

    # Day-by-day (only active days)
    active_days = [d for d in report["daily"] if d["spent"] > 0 or d["received"] > 0]
    if active_days:
        lines.append("📆 Daily breakdown:")
        for day in active_days:
            parts = []
            if day["received"] > 0:
                parts.append(f"+₹{day['received']:,.0f}")
            if day["spent"] > 0:
                parts.append(f"-₹{day['spent']:,.0f}")
            lines.append(f"  {day['date']}: {' | '.join(parts)}")
        lines.append("")

    lines.append("_Sent by Orion — your finance assistant_")
    return "\n".join(lines)


def generate_pdf(report: dict, output_dir: str = "data/reports") -> str:
    """Generate a PDF report. Returns the file path."""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"report_{report['start']}_{report['end']}.pdf"
    path = os.path.join(output_dir, filename)

    c = canvas.Canvas(path, pagesize=A4)
    _, height = A4
    y = height - 60

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "Orion — Financial Report")
    y -= 30

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Period: {report['start']} to {report['end']}")
    y -= 30

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Summary")
    y -= 20

    c.setFont("Helvetica", 12)
    rows: list[tuple[str, str]] = [
        ("Total Received", f"Rs {report['received']:,.2f}"),
        ("Total Spent", f"Rs {report['spent']:,.2f}"),
        ("Net", f"Rs {report['net']:+,.2f}"),
        ("Transactions", str(report["transaction_count"])),
    ]
    if report["top_category"]:
        rows.append(("Top Category", f"{str(report['top_category']).title()} (Rs {report['top_cat_amount']:,.0f})"))
    if report["top_sender"]:
        rows.append(("Top Sender", f"{report['top_sender']} (Rs {report['top_sender_amount']:,.0f})"))

    for label, value in rows:
        c.drawString(70, y, f"{label}:")
        c.drawString(250, y, value)
        y -= 18

    y -= 15
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Day-by-Day")
    y -= 20
    c.setFont("Helvetica", 11)
    for day in report["daily"]:
        if day["spent"] > 0 or day["received"] > 0:
            c.drawString(
                70, y,
                f"{day['date']}   Spent: Rs {day['spent']:,.0f}   Received: Rs {day['received']:,.0f}"
            )
            y -= 16
            if y < 80:
                c.showPage()
                y = height - 60

    c.save()
    return path
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
