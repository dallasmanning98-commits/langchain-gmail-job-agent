from __future__ import annotations

from pathlib import Path
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

HEADERS = [
    "Date",
    "Company",
    "Position",
    "Location",
    "Pay Range",
    "Source",
    "Status",
    "Priority",
    "Fit Score",
    "Next Action",
    "Notes",
    "Gmail URL",
    "Message ID",
]


def _normalize(value) -> str:
    return str(value or "").strip().lower()


def open_or_create_tracker(path: Path):
    if path.exists():
        wb = load_workbook(path)
        ws = wb[wb.sheetnames[0]]
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = "Job Leads"
        ws.append(HEADERS)
    return wb, ws


def ensure_headers(ws):
    existing = [cell.value for cell in ws[1]]
    if not any(existing):
        for idx, header in enumerate(HEADERS, start=1):
            ws.cell(row=1, column=idx).value = header
    else:
        for header in HEADERS:
            if header not in existing:
                ws.cell(row=1, column=ws.max_column + 1).value = header

    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F4E78")
        cell.alignment = Alignment(horizontal="center")


def header_map(ws) -> dict[str, int]:
    return {_normalize(cell.value): cell.column for cell in ws[1] if cell.value}


def existing_message_ids(ws) -> set[str]:
    hm = header_map(ws)
    col = hm.get("message id")
    if not col:
        return set()
    return {str(ws.cell(row=r, column=col).value) for r in range(2, ws.max_row + 1) if ws.cell(row=r, column=col).value}


def append_leads(path: Path, leads: list[dict]) -> int:
    wb, ws = open_or_create_tracker(path)
    ensure_headers(ws)
    hm = header_map(ws)
    seen = existing_message_ids(ws)
    added = 0

    for item in leads:
        if item.get("Message ID") in seen:
            continue
        row = ws.max_row + 1
        for key, value in item.items():
            col = hm.get(_normalize(key))
            if col:
                ws.cell(row=row, column=col).value = value
        added += 1

    for col in range(1, ws.max_column + 1):
        letter = get_column_letter(col)
        ws.column_dimensions[letter].width = min(max(14, len(str(ws.cell(row=1, column=col).value or "")) + 3), 45)
    for row in range(2, ws.max_row + 1):
        ws.cell(row=row, column=hm.get("notes", 11)).alignment = Alignment(wrap_text=True, vertical="top")
        ws.cell(row=row, column=hm.get("next action", 10)).alignment = Alignment(wrap_text=True, vertical="top")

    wb.save(path)
    return added
