# (Expense Tracker, Version 1)
# Data is stored in data/expenses.csv.
# Features:
# - Add expense (date, amount, category, description)
# - View expenses with index + optional filters (category, date range, text)
# - Edit entry by index
# - Delete entry by index, or delete last (undo)
# - Summaries: by category, by date, by month (YYYY-MM)
# - Show grand total across all expenses
# - Export last viewed rows to data/reports/<timestamp>_export.csv


from __future__ import annotations
import csv
import os
import datetime as dt
from typing import List, Dict, Iterable, Optional

# ---------- Paths / constants ----------
CSV_DIR = "data"
REPORTS_DIR = os.path.join(CSV_DIR, "reports")
CSV = os.path.join(CSV_DIR, "expenses.csv")
HEADERS = ["Date", "Amount", "Category", "Description"]


# ---------- Setup & utilities ----------
def ensure_dirs_and_csv() -> None:
    """Create data/ and reports/ folders, and ensure expenses.csv has a header row."""
    os.makedirs(CSV_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    need_header = not os.path.exists(CSV) or os.path.getsize(CSV) == 0
    if need_header:
        with open(CSV, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(HEADERS)


def read_rows(include_header: bool = False) -> List[List[str]]:
    """Read all rows from CSV; returns list of rows (each row is a list of strings)."""
    ensure_dirs_and_csv()
    with open(CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if not include_header and rows and rows[0] == HEADERS:
        return rows[1:]
    return rows


def write_rows(rows: List[List[str]]) -> None:
    """Overwrite CSV with HEADERS + rows."""
    with open(CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEADERS)
        w.writerows(rows)


def parse_iso_date(s: str) -> dt.date:
    """Parse YYYY-MM-DD to date (raises ValueError on bad format)."""
    return dt.date.fromisoformat(s)


def ask_date(prompt: str = "Date (YYYY-MM-DD) [today]: ", default_today: bool = True) -> str:
    """Ask for date; empty => today (if default_today). Returns ISO string."""
    while True:
        raw = input(prompt).strip()
        if not raw and default_today:
            return dt.date.today().isoformat()
        try:
            return parse_iso_date(raw).isoformat()
        except ValueError:
            print("❗ Please use YYYY-MM-DD (e.g., 2025-09-25).")


def ask_optional_date(prompt: str) -> Optional[str]:
    """Ask for optional date; empty => None."""
    while True:
        raw = input(prompt).strip()
        if not raw:
            return None
        try:
            return parse_iso_date(raw).isoformat()
        except ValueError:
            print("❗ Please use YYYY-MM-DD or leave blank.")


def ask_amount() -> float:
    """
    Ask for a numeric amount.
    Accepts '12.50' and '12,50' (comma converted to dot). Returns rounded float.
    """
    while True:
        raw = input("Amount: ").strip().replace(",", ".")
        try:
            return round(float(raw), 2)
        except ValueError:
            print("❗ Amount must be a number (e.g., 12.50).")


def input_with_default(prompt: str, default: str) -> str:
    """Prompt with a default value shown in brackets; empty keeps default."""
    raw = input(f"{prompt} [{default}]: ").strip()
    return raw if raw else default


def format_money(x: str | float) -> str:
    """Render value as money-like with 2 decimals where possible."""
    try:
        return f"{float(x):.2f}"
    except Exception:
        return str(x)


# ---------- Table formatting ----------
def _format_table_generic(all_rows: List[List[str]]) -> str:
    """Format any 2D list (includes header in row[0]) into a simple left-aligned table."""
    if not all_rows:
        return ""
    cols = list(zip(*all_rows))
    widths = [max(len(str(cell)) for cell in col) for col in cols]

    def fmt_row(row: Iterable[str]) -> str:
        cells = [str(c).ljust(w) for c, w in zip(row, widths)]
        return " | ".join(cells)

    line = "-+-".join("-" * w for w in widths)
    out = [fmt_row(all_rows[0]), line]
    for r in all_rows[1:]:
        out.append(fmt_row(r))
    return "\n".join(out)


def format_expense_table(rows: List[List[str]], show_index: bool = True) -> str:
    """Format expense rows with headers and optional index column."""
    if not rows:
        return "No expenses yet."
    header = (["#"] if show_index else []) + HEADERS
    display = [header]
    for idx, r in enumerate(rows):
        r = r[:]  
        r[1] = format_money(r[1])
        line = ([str(idx)] if show_index else []) + r
        display.append(line)
    return _format_table_generic(display)


# ---------- Core actions ----------
def add_expense() -> None:
    """Collect a single expense from user and append to CSV."""
    date = ask_date()
    amt = ask_amount()
    cat = input("Category (e.g., Food, Transport): ").strip() or "General"
    desc = input("Description: ").strip()
    with open(CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([date, amt, cat, desc])
    print("✅ Saved.\n")


def delete_last_entry() -> None:
    """Remove the last data row from the CSV (simple undo)."""
    rows = read_rows()
    if not rows:
        print("No expenses to delete.\n")
        return
    last = rows.pop()
    write_rows(rows)
    print(f"🗑️ Deleted last entry: {last}\n")


def delete_by_index() -> None:
    """Delete a specific row by its index (as shown in the table)."""
    rows = read_rows()
    if not rows:
        print("No expenses to delete.\n")
        return
    print(format_expense_table(rows))
    try:
        idx = int(input("Enter index (#) to delete: ").strip())
        if idx < 0 or idx >= len(rows):
            print("❗ Invalid index.\n")
            return
    except ValueError:
        print("❗ Please enter a number.\n")
        return
    deleted = rows.pop(idx)
    write_rows(rows)
    print(f"🗑️ Deleted: {deleted}\n")


def edit_by_index() -> None:
    """
    Edit a specific row by index.
    Prompts each field with its current value as default.
    """
    rows = read_rows()
    if not rows:
        print("No expenses to edit.\n")
        return
    print(format_expense_table(rows))
    try:
        idx = int(input("Enter index (#) to edit: ").strip())
        if idx < 0 or idx >= len(rows):
            print("❗ Invalid index.\n")
            return
    except ValueError:
        print("❗ Please enter a number.\n")
        return

    date, amt, cat, desc = rows[idx]

    
    while True:
        new_date = input_with_default("Date (YYYY-MM-DD)", date)
        try:
            parse_iso_date(new_date)
            break
        except ValueError:
            print("❗ Please use YYYY-MM-DD.")

    while True:
        amt_raw = input_with_default("Amount", format_money(amt)).replace(",", ".")
        try:
            new_amt = f"{round(float(amt_raw), 2):.2f}"
            break
        except ValueError:
            print("❗ Amount must be a number.")

    new_cat = input_with_default("Category", cat or "General")
    new_desc = input_with_default("Description", desc)

    rows[idx] = [new_date, new_amt, new_cat, new_desc]
    write_rows(rows)
    print("✏️ Updated.\n")


# ---------- Filters and views ----------
def filter_rows(
    rows: List[List[str]],
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    text: Optional[str] = None,
) -> List[List[str]]:
    """Return rows filtered by category, date range [start, end], and substring text in any field."""
    def in_range(d: str) -> bool:
        ok_start = (start_date is None) or (d >= start_date)
        ok_end = (end_date is None) or (d <= end_date)
        return ok_start and ok_end

    out: List[List[str]] = []
    for r in rows:
        d, amt, cat, desc = r
        if category and cat.lower() != category.lower():
            continue
        if not in_range(d):
            continue
        if text:
            blob = " ".join(map(str, r)).lower()
            if text.lower() not in blob:
                continue
        out.append(r)
    return out


def view_expenses() -> List[List[str]]:

    rows = read_rows()
    if not rows:
        print("No expenses yet.\n")
        return []

    # Ask filters
    use_filters = input("Apply filters? (y/N): ").strip().lower() == "y"
    cat = None
    sdate = None
    edate = None
    text = None
    if use_filters:
        cat_in = input("Category filter (blank = all): ").strip()
        cat = cat_in or None
        sdate = ask_optional_date("Start date (YYYY-MM-DD) [blank = none]: ")
        edate = ask_optional_date("End date   (YYYY-MM-DD) [blank = none]: ")
        text_in = input("Text search (in any field, blank = none): ").strip()
        text = text_in or None

    rows = filter_rows(rows, category=cat, start_date=sdate, end_date=edate, text=text)
    if not rows:
        print("No matching expenses.\n")
        return []

    print(format_expense_table(rows))
    print()
    return rows


# ---------- Summaries ----------
def summarize_by_category() -> None:
    """Print total amount grouped by Category."""
    rows = read_rows()
    if not rows:
        print("No expenses yet.\n")
        return

    totals: Dict[str, float] = {}
    for date, amt, cat, desc in rows:
        try:
            totals[cat] = totals.get(cat, 0.0) + float(amt)
        except ValueError:
            continue

    header = ["Category", "Total"]
    data = [[cat, f"{totals[cat]:.2f}"] for cat in sorted(totals)]
    print(_format_table_generic([header] + data))
    print()


def summarize_by_date() -> None:
    """Print total amount grouped by Date (YYYY-MM-DD)."""
    rows = read_rows()
    if not rows:
        print("No expenses yet.\n")
        return

    totals: Dict[str, float] = {}
    for date, amt, cat, desc in rows:
        try:
            totals[date] = totals.get(date, 0.0) + float(amt)
        except ValueError:
            continue

    header = ["Date", "Total"]
    data = [[d, f"{totals[d]:.2f}"] for d in sorted(totals)]
    print(_format_table_generic([header] + data))
    print()


def summarize_by_month() -> None:
    """Print total amount grouped by month (YYYY-MM)."""
    rows = read_rows()
    if not rows:
        print("No expenses yet.\n")
        return

    totals: Dict[str, float] = {}
    for date, amt, cat, desc in rows:
        month = (date or "")[:7]  
        try:
            totals[month] = totals.get(month, 0.0) + float(amt)
        except ValueError:
            continue

    header = ["Month (YYYY-MM)", "Total"]
    data = [[m, f"{totals[m]:.2f}"] for m in sorted(totals)]
    print(_format_table_generic([header] + data))
    print()


def show_total() -> None:
    """Print the overall total of all expenses."""
    rows = read_rows()
    if not rows:
        print("No expenses yet.\n")
        return
    total = 0.0
    for date, amt, cat, desc in rows:
        try:
            total += float(amt)
        except ValueError:
            continue
    print(f"💵 Overall total = {total:.2f}\n")


# ---------- Export ----------
def export_rows(rows: List[List[str]]) -> None:
    """Export given rows to a timestamped CSV under data/reports/."""
    if not rows:
        print("Nothing to export.\n")
        return
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(REPORTS_DIR, f"{ts}_export.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEADERS)
        w.writerows(rows)
    print(f"📄 Exported {len(rows)} rows to: {path}\n")


# ---------- Main menu ----------
def main() -> None:
    """Menu loop (simple CLI)."""
    ensure_dirs_and_csv()
    last_view: List[List[str]] = []  # store last viewed rows for quick export

    while True:
        print("1) Add expense")
        print("2) View expenses (with optional filters)")
        print("3) Summary by category")
        print("4) Summary by date")
        print("5) Summary by month")
        print("6) Show total of all expenses")
        print("7) Edit entry by index")
        print("8) Delete entry by index")
        print("9) Delete last entry (undo)")
        print("10) Export last viewed rows")
        print("11) Quit")
        choice = input("> ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            last_view = view_expenses()
        elif choice == "3":
            summarize_by_category()
        elif choice == "4":
            summarize_by_date()
        elif choice == "5":
            summarize_by_month()
        elif choice == "6":
            show_total()
        elif choice == "7":
            edit_by_index()
        elif choice == "8":
            delete_by_index()
        elif choice == "9":
            delete_last_entry()
        elif choice == "10":
            if not last_view:
                print("Tip: choose 'View expenses' first to select what to export.\n")
            export_rows(last_view)
        elif choice == "11":
            break
        else:
            print("Try 1–11.\n")


# ---------- Entry point ----------
if __name__ == "__main__":
    main()
