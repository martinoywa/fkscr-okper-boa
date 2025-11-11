import argparse
import asyncio
import os

import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from crawler.crawler import crawl_page, generate_daily_report
from db.db import DB, get_last_page
from utils.utils import logger

load_dotenv()

SCHEDULER_CRAWL_HOUR = int(os.getenv("SCHEDULER_CRAWL_HOUR"))
SCHEDULER_CRAWL_MINUTE = int(os.getenv("SCHEDULER_CRAWL_MINUTE"))


async def run_crawl(generate_report, report_format):
    logger.info("Starting scheduled crawl...")
    async with aiohttp.ClientSession() as session:
        page = await get_last_page(DB)
        while True:
            success = await crawl_page(session, DB, page)
            if not success:
                break
            page += 1
    logger.info("Scheduled crawl finished.")

    if generate_report:
        await generate_daily_report(report_format)
        logger.info("Daily change report generated successfully.")


def start_scheduler(generate_report, report_format):
    """
    Start the APScheduler AsyncIO scheduler.
    This is the main entry point for the project.
    """
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_crawl, "cron",
                      hour=SCHEDULER_CRAWL_HOUR, minute=SCHEDULER_CRAWL_MINUTE,
                      args=[generate_report, report_format])
    scheduler.start()

    logger.info("Scheduler started. Waiting for jobs...")
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Book Crawler Scheduler.")
    parser.add_argument(
        "--generate-report",
        type=bool,
        help="Generate a daily change report after each crawl."
    )
    parser.add_argument(
        "--report-format",
        choices=["csv", "json"],
        default="csv",
        help="Format for the daily change report (csv or json). Default: csv"
    )
    args = parser.parse_args()

    start_scheduler(args.generate_report, args.report_format)
