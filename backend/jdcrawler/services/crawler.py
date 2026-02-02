import asyncio
from typing import List, Type

from jdcrawler.crawlers.base import BaseCrawler
from jdcrawler.crawlers.jobkorea import JobkoreaCrawler
from jdcrawler.crawlers.saramin import SaraminCrawler
from jdcrawler.crawlers.wanted import WantedCrawler
from jdcrawler.db.client import DatabaseClient
from jdcrawler.models.job import JobCreate


class CrawlerService:
    def __init__(self, db: DatabaseClient):
        self.db = db
        self.crawlers: dict[str, Type[BaseCrawler]] = {
            "saramin": SaraminCrawler,
            "jobkorea": JobkoreaCrawler,
            "wanted": WantedCrawler,
        }

    async def crawl_keyword(
        self, keyword: str, sites: List[str] | None = None, headless: bool = True
    ) -> int:
        if sites is None:
            sites = list(self.crawlers.keys())

        total_crawled = 0

        for site in sites:
            crawler_cls = self.crawlers.get(site)
            if not crawler_cls:
                continue

            print(f"Crawling {site} for '{keyword}'...")
            crawler = crawler_cls(headless=headless)
            try:
                async with crawler as cr:
                    jobs = await cr.crawl(keyword)
                    for job in jobs:
                        self.db.create_job(job)
                    count = len(jobs)
                    print(f"Saved {count} jobs from {site}")
                    total_crawled += count
            except Exception as e:
                print(f"Error crawling {site} for {keyword}: {e}")
                # Log traceback but continue to next site
                import traceback
                traceback.print_exc()

        return total_crawled

    async def crawl_all_active_keywords(self, headless: bool = True):
        keywords = self.db.get_keywords(only_active=True)
        print(f"Found {len(keywords)} active keywords.")
        
        if not keywords:
            print("No active keywords to crawl.")
            return

        for kw in keywords:
            await self.crawl_keyword(kw.keyword, headless=headless)
