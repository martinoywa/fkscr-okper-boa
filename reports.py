import asyncio
import logging
from datetime import datetime, timedelta
import pandas as pd
from db import DB, CHANGELOG_COLLECTION, fetch_changes_for_day
from utils import flatten_changes


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("crawler.log", encoding="utf-8")
    ]
)


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
    logging.info(df.head(10))  # preview


def main():
    """
    Entry point: just runs for today's date automatically.
    Default output format = CSV
    """
    asyncio.run(generate_daily_report(fmt="csv"))


if __name__ == "__main__":
    main()
