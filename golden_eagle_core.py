# golden_eagle_core.py
"""
Backend for عقاب زرین (Golden Eagle) time‑entry system.
Handles data structure, JSON persistence, validation, and report generation.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import csv
import io

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# =========================== DATA MODEL ===========================

def create_empty_day_record(year: int, month: int, day: int,
                            weekday: str = "",
                            day_type: str = "عادی",
                            in_time: str = "",
                            out_time: str = "",
                            tasks: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """
    Create a new day record.
    tasks: list of dicts with keys: name, hours, description, subtasks (list of same structure)
    """
    return {
        "year": year,
        "month": month,
        "day": day,
        "weekday": weekday,          # e.g., "شنبه"
        "day_type": day_type,        # "عادی", "مرخصی", "تعطیل رسمی", "اضافه کار", "دورکاری"
        "in_time": in_time,          # HH:MM
        "out_time": out_time,        # HH:MM
        "tasks": tasks or []         # list of task dicts
    }


def get_date_key(record: Dict) -> str:
    """Return a string key for sorting/lookup, e.g., '1403-01-01'."""
    return f"{record['year']:04d}-{record['month']:02d}-{record['day']:02d}"


def get_total_actual_hours(record: Dict) -> float:
    """Return actual working hours based on in/out times."""
    if record["day_type"] in ("تعطیل رسمی",):
        return 0.0
    if record["day_type"] == "مرخصی":
        return 8.0  # standard
    if record["day_type"] == "دورکاری":
        # actual is sum of task hours (computed elsewhere)
        return sum_task_hours(record)
    # normal or اضافه کار: compute from in/out
    try:
        in_h, in_m = map(int, record["in_time"].split(":"))
        out_h, out_m = map(int, record["out_time"].split(":"))
        total_minutes = (out_h * 60 + out_m) - (in_h * 60 + in_m)
        return total_minutes / 60.0
    except:
        return 0.0


def sum_task_hours(record: Dict) -> float:
    """Sum all task and subtask hours."""
    total = 0.0
    for task in record.get("tasks", []):
        # If task has subtasks, sum them; else use task's own hours
        if "subtasks" in task and task["subtasks"]:
            for sub in task["subtasks"]:
                total += float(sub.get("hours", 0.0))
        else:
            total += float(task.get("hours", 0.0))
    return total


def validate_day(record: Dict) -> Tuple[bool, List[str]]:
    """
    Check consistency:
    - For normal/اضافه کار: actual hours = in/out diff.
    - For دورکاری: actual = sum tasks.
    - For تعطیل رسمی: actual = 0, no tasks.
    - For مرخصی: no tasks needed, actual = 8.
    - Check that sum(task hours) is consistent with expected.
    Returns (is_valid, list_of_warnings/errors)
    """
    errors = []
    day_type = record.get("day_type", "")
    tasks = record.get("tasks", [])
    total_task_hours = sum_task_hours(record)

    if day_type == "تعطیل رسمی":
        if total_task_hours > 0:
            errors.append("روز تعطیل نباید تسک داشته باشد.")
        return len(errors)==0, errors

    if day_type == "مرخصی":
        if total_task_hours > 0:
            errors.append("روز مرخصی نباید تسک داشته باشد.")
        # actual = 8
        return len(errors)==0, errors

    # For other types, compute actual from in/out or from tasks
    if day_type in ("عادی", "اضافه کار"):
        try:
            actual = get_total_actual_hours(record)
        except:
            errors.append("ورود و خروج معتبر نیست.")
            return False, errors
        expected_standard = 8.0  # standard for عادی and اضافه کار? Actually اضافه کار also has standard? We'll treat same.
        # We don't check actual vs standard here, we just compare task sum to actual
        if abs(total_task_hours - actual) > 0.01:
            errors.append(f"مجموع ساعات تسک‌ها ({total_task_hours:.2f}) با ساعت کارکرد ({actual:.2f}) همخوانی ندارد.")
        # Also compute shortfall/overwork later.
    elif day_type == "دورکاری":
        # actual = total_task_hours
        actual = total_task_hours
        # no in/out check
        pass
    else:
        errors.append(f"نوع روز نامعتبر: {day_type}")

    return len(errors)==0, errors


def compute_shortfall_overwork(record: Dict, standard_hours: float = 8.0) -> Tuple[float, float]:
    """
    Return (shortfall, overwork) based on actual hours vs standard.
    For تعطیل رسمی: both 0.
    For مرخصی: actual = 8, so 0,0.
    For دورکاری: actual = sum tasks, compare to standard.
    """
    day_type = record.get("day_type", "")
    if day_type == "تعطیل رسمی":
        return 0.0, 0.0
    if day_type == "مرخصی":
        return 0.0, 0.0  # assuming standard 8
    if day_type in ("عادی", "اضافه کار", "دورکاری"):
        actual = get_total_actual_hours(record)
        diff = actual - standard_hours
        if diff < 0:
            return -diff, 0.0
        else:
            return 0.0, diff
    return 0.0, 0.0


# =========================== JSON I/O ===========================

DATA_FILE = "golden_eagle_data.json"

def load_all_days() -> Dict[str, Dict]:
    """Load all day records, keyed by date string (YYYY-MM-DD)."""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Convert list to dict by date key
    return {get_date_key(rec): rec for rec in data}


def save_all_days(records: Dict[str, Dict]):
    """Save all records to JSON."""
    data = list(records.values())
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================== REPORT GENERATION ===========================

def generate_monthly_report(year: int, month: int, all_records: Dict[str, Dict]) -> Tuple[str, str]:
    """
    Generate CSV and PDF for the given month.
    Returns (csv_string, pdf_bytes) or (None, None) if no data.
    """
    # Filter records for that month
    month_records = [rec for rec in all_records.values()
                     if rec["year"] == year and rec["month"] == month]
    if not month_records:
        return None, None

    # Sort by day
    month_records.sort(key=lambda r: r["day"])

    # Build CSV rows
    header = ["تاریخ", "روز هفته", "نوع روز", "ورود", "خروج", "کارکرد", "کسری", "اضافه کار", "تسک‌ها", "وضعیت"]
    rows = [header]
    for rec in month_records:
        date_str = f"{rec['day']}/{rec['month']}/{rec['year']}"
        weekday = rec.get("weekday", "")
        day_type = rec.get("day_type", "")
        in_time = rec.get("in_time", "")
        out_time = rec.get("out_time", "")
        actual = get_total_actual_hours(rec)
        short, over = compute_shortfall_overwork(rec)
        tasks_str = "; ".join([f"{t['name']}: {t.get('hours',0)}" for t in rec.get("tasks", [])])
        valid, errors = validate_day(rec)
        status = "صحیح" if valid else "خطا: " + "، ".join(errors)
        rows.append([date_str, weekday, day_type, in_time, out_time,
                     f"{actual:.2f}", f"{short:.2f}", f"{over:.2f}", tasks_str, status])

    # Generate CSV string
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerows(rows)
    csv_data = csv_buffer.getvalue()

    # Generate PDF using reportlab if available
    pdf_data = None
    if REPORTLAB_AVAILABLE:
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title = f"گزارش ماه {month} سال {year}"
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Spacer(1, 12))

        # Table
        table_data = []
        # header style
        table_data.append([Paragraph(cell, styles['Heading5']) for cell in header])
        for row in rows[1:]:
            table_data.append([Paragraph(cell, styles['Normal']) for cell in row])

        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(table)
        doc.build(elements)
        pdf_data = pdf_buffer.getvalue()

    return csv_data, pdf_data