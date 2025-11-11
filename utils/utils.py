import hashlib
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/crawler.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger("book_scraper")


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
