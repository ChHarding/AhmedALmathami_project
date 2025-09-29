# Bug Log

- 2025-09-26: Entering "12,50" works, but not all locales use commas — may revisit in V2.
- 2025-09-26: Editing by index doesn’t validate empty category well. TODO.
- 2025-09-26: If `expenses.csv` is deleted while the app is running, the next `view` causes an error until restart. Fix by re-checking file before each read. (V2)
- 2025-09-26: Export creates CSV with timestamp, but filename can get very long. Consider shorter names (e.g., `YYYYMMDD_export.csv`). (V2)
- 2025-09-26: View table misaligns if category or description text is very long. Could add truncation or wrapping. (V2)
- 2025-09-26: Summaries skip rows if Amount field contains invalid text (e.g., "ten"). Should warn user when saving. (V2)
- 2025-09-26: Deleting last entry after filtering may confuse users (they expect to delete last *filtered* row, not actual last row). Clarify in menu or fix in V2.
- 2025-09-26: No confirmation before deleting an entry — easy to delete by mistake. Add a "Are you sure? (y/n)" prompt in V2.
- 2025-09-26: Program quits immediately on `Ctrl+C`. Could catch KeyboardInterrupt and show "Goodbye" instead of stack trace. (V2)
- 2025-09-26: `show_total()` prints sum but doesn’t format with commas (e.g., 1,000.00). Add formatting for readability. (V2)
