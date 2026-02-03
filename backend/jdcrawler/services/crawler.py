import asyncio
from typing import List, Type

from jdcrawler.crawlers.base import BaseCrawler
from jdcrawler.crawlers.jobkorea import JobkoreaCrawler
from jdcrawler.crawlers.saramin import SaraminCrawler
from jdcrawler.crawlers.wanted import WantedCrawler
from jdcrawler.db.client import DatabaseClient
from jdcrawler.db.schema import JobTable
from jdcrawler.models.job import JobCreate
from jdcrawler.services.analysis import AnalysisService


class CrawlerService:
    def __init__(self, db: DatabaseClient):
        self.db = db
        self.analysis_service = AnalysisService()
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

        # Get user profile once for analysis
        profile = self.db.get_profile()

        total_crawled = 0

        for site in sites:
            crawler_cls = self.crawlers.get(site)
            if not crawler_cls:
                continue

            print(f"Crawling {site} for '{keyword}'...")
            # Use 10-15s jittered delay to avoid temporary bans
            crawler = crawler_cls(headless=headless, rate_limit_delay=10.0, jitter=5.0)
            try:
                async with crawler as cr:
                    jobs_data = await cr.crawl(keyword)
                    
                    # For each job, we need to enrich and analyze
                    # To speed up, we can do this in chunks or after initial save
                    for job_create in jobs_data:
                        # 1. Check if job already exists
                        existing_job = self.db.jobs_session.query(JobTable).filter(JobTable.url == job_create.url).first()
                        
                        # 2. Enrich if new job OR if existing job has no description
                        if not existing_job or not existing_job.description:
                            if hasattr(cr, 'extract_details'):
                                print(f"  Enriching details for: {job_create.title[:30]}...")
                                details = await cr.extract_details(job_create.url)
                                job_create.description = details.get("description")
                                job_create.description_image_url = details.get("description_image_url")
                        
                        # 3. Phase 1: Rule-based filtering (If it's a new job or was updated)
                        if job_create.description:
                             # Initialize score to 0 instead of None
                             job_create.ai_score = 0
                             job_create.ai_status = "pending"
                             
                             # Check for exclude keywords
                             is_filtered = False
                             for ex_kw in profile.exclude_keywords:
                                 if ex_kw.lower() in (job_create.title + (job_create.description or "")).lower():
                                     job_create.ai_score = 0
                                     job_create.ai_summary = f"제외 키워드 '{ex_kw}' 포함됨"
                                     job_create.ai_status = "filtered"
                                     is_filtered = True
                                     break
                             
                             if not is_filtered:
                                 match_count = 0
                                 if profile.tech_stack:
                                     for skill in profile.tech_stack:
                                         if skill.name.lower() in (job_create.title + (job_create.description or "")).lower():
                                             match_count += 1
                                     
                                     total_tech = len(profile.tech_stack)
                                     job_create.ai_score = int((match_count / total_tech) * 100)
                                 else:
                                     job_create.ai_score = 0
                        
                        # 4. Save/Update in DB
                        if existing_job:
                            # Update missing fields
                            if not existing_job.description and job_create.description:
                                existing_job.description = job_create.description
                                existing_job.description_image_url = job_create.description_image_url
                                existing_job.ai_score = job_create.ai_score
                                existing_job.ai_status = job_create.ai_status
                                existing_job.ai_summary = job_create.ai_summary
                                self.db.jobs_session.commit()
                        else:
                            self.db.create_job(job_create)
                        
                    count = len(jobs_data)
                    print(f"Saved and analyzed {count} jobs from {site}")
                    total_crawled += count
            except Exception as e:
                print(f"Error crawling {site} for {keyword}: {e}")
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
