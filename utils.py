import hashlib
import json
import os


CHECKPOINT_FILE = "checkpoint.json"

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
