# scheduler.py
import asyncio
import logging

import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from crawler import crawl_page
from db import DB, get_last_page


# Run every day at 11:40 server time
CRAWL_HOUR = 11
CRAWL_MINUTE = 40


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


async def run_crawl():
    logging.info("Starting scheduled crawl...")
    async with aiohttp.ClientSession() as session:
        page = await get_last_page(DB)
        while True:
            success = await crawl_page(session, DB, page)
            if not success:
                break
            page += 1
    logging.info("Scheduled crawl finished.")


def start_scheduler():
    """
    Start the APScheduler AsyncIO scheduler.
    This is the main entry point for the project.
    """
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_crawl, "cron", hour=CRAWL_HOUR, minute=CRAWL_MINUTE)
    scheduler.start()

    logging.info("Scheduler started. Waiting for jobs...")
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped.")


if __name__ == "__main__":
    start_scheduler()
