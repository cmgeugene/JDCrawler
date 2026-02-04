from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from jdcrawler.db.client import DatabaseClient
from jdcrawler.services.crawler import CrawlerService

scheduler = AsyncIOScheduler()


import os

async def run_crawl_job():
    print("Starting scheduled crawl...")
    db = DatabaseClient()
    try:
        service = CrawlerService(db)
        # Use HEADLESS env var, default to True
        headless = os.getenv("HEADLESS", "true").lower() == "true"
        await service.crawl_all_active_keywords(headless=headless)
    except Exception as e:
        print(f"Scheduled crawl failed: {e}")
    finally:
        db.close()
    print("Scheduled crawl finished.")


def start_scheduler():
    if not scheduler.running:
        # Run every 4 hours
        scheduler.add_job(
            run_crawl_job,
            IntervalTrigger(hours=4),
            id="crawl_all",
            replace_existing=True,
        )
        scheduler.start()
        print("Scheduler started. Crawling every 4 hours.")
