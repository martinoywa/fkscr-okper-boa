import hashlib
import json
import logging
import os
from datetime import datetime

import pandas as pd

from db import fetch_changes_for_day

CHECKPOINT_FILE = "checkpoint.json"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("crawler.log", encoding="utf-8")
    ]
)


def load_checkpoint():
    """Read last crawled page number from checkpoint.json"""
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r") as f:
                data = json.load(f)
                return data.get("last_page", 1)
        except Exception:
            return 1
    return 1


def save_checkpoint(page_number):
    """Save last successfully crawled page number."""
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"last_page": page_number}, f)


def build_fingerprint(doc):
    """Return a string fingerprint for a book."""
    parts = [
        doc.get("name", ""),
        doc.get("price_excl_tax", ""),
        doc.get("price_incl_tax", ""),
        doc.get("availability", ""),
        str(doc.get("rating", "")),
        doc.get("number_of_reviews", ""),
    ]
    return "|".join(parts)


def compute_hash(doc):
    fingerprint = build_fingerprint(doc)
    return hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()


def build_changed_content(current_doc, existing_doc):
    """Returns the dictionary of changes"""
    changed_content = {}

    tracked_fields = [
        "name",
        "price_excl_tax",
        "price_incl_tax",
        "availability",
        "rating",
        "number_of_reviews",
    ]

    for field in tracked_fields:
        old_val = existing_doc.get(field)
        new_val = current_doc.get(field)
        if old_val != new_val:
            changed_content[field] = {"old": old_val, "new": new_val}

    return changed_content


def flatten_changes(records):
    """
    Generate a list of dictionaries, each representing a change.
    """
    flat_rows = []
    for r in records:
        base = {
            "book_url": r.get("book_url"),
            "book_name": r.get("book_name"),
            "change_type": r.get("change_type"),
            "changed_at": r.get("changed_at"),
        }

        changes = r.get("changes") or {}
        if not changes: # New books
            flat_rows.append({**base, "field": None, "old_value": None, "new_value": None})
        else:
            for field, vals in changes.items():
                flat_rows.append({
                    **base,
                    "field": field,
                    "old_value": vals.get("old"),
                    "new_value": vals.get("new"),
                })
    return flat_rows


async def generate_daily_report(format="csv"):
    """
    Generate a daily change report based on the current date.
    Saves to CSV or JSON using pandas.
    """
    # Automatically use current day's date
    today = datetime.utcnow()
    date_str = today.strftime("%Y-%m-%d")

    logging.info(f"Generating daily change report for {date_str}...")

    # Fetch and flatten change records
    records = await fetch_changes_for_day(today)
    if not records:
        logging.info(f"No changes found for {date_str}. Nothing to report.")
        return

    flat_records = flatten_changes(records)
    df = pd.DataFrame(flat_records)

    # File name
    filename = f"change_report_{date_str}.{format}"

    # Save report
    if format == "csv":
        df.to_csv(filename, index=False, encoding="utf-8")
    elif format == "json":
        df.to_json(filename, orient="records", indent=2, date_format="iso")
    else:
        raise ValueError("Format must be 'csv' or 'json'")

    logging.info(f"Change report saved to: {filename}")
