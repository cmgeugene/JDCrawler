import asyncio
import json
import httpx
from urllib.parse import quote
from bs4 import BeautifulSoup

from jdcrawler.crawlers.base import BaseCrawler
from jdcrawler.models.job import JobCreate, JobSite


class WantedCrawler(BaseCrawler):
    def __init__(self, headless: bool = True, rate_limit_delay: float = 3.0, **kwargs):
        super().__init__(headless, rate_limit_delay, **kwargs)
        self.base_url = "https://www.wanted.co.kr/search"

    async def crawl(self, keyword: str) -> list[JobCreate]:
        # Explicitly encode keyword for URL
        encoded_keyword = quote(keyword)
        url = f"{self.base_url}?query={encoded_keyword}"
        
        # Use the testid from provided HTML for more reliable waiting
        try:
            html = await self.fetch_page(
                url, 
                wait_until="load", 
                wait_for_selector="div[data-testid='SearchPositionListContainer']", 
                timeout=30000
            )
            await asyncio.sleep(2) # Buffer for JS rendering
        except Exception as e:
            print(f"Warning: Wanted list container timeout, attempting fallback: {e}")
            html = await self.fetch_page(url, wait_until="load", wait_for_selector="a[href*='/wd/']", timeout=20000)
             
        jobs = self._parse_jobs(html)
        return jobs

    def _parse_jobs(self, html: str) -> list[JobCreate]:
        soup = BeautifulSoup(html, "html.parser")
        # Target the specific role and classes from the HTML snippet
        job_cards = soup.select("div[role='listitem']")
        jobs = []
        seen_urls = set()

        for card in job_cards:
            link_elem = card.select_one("a[href*='/wd/']")
            if not link_elem:
                continue
                
            href = link_elem.get("href", "")
            if not href or href in seen_urls:
                continue
            seen_urls.add(href)

            # Accurate selectors from the provided HTML
            title_elem = card.select_one("strong[class*='JobCard_title']")
            company_elem = card.select_one("span[class*='CompanyNameWithLocationPeriod_CompanyNameWithLocationPeriod__company']")
            location_elem = card.select_one("span[class*='CompanyNameWithLocationPeriod_CompanyNameWithLocationPeriod__location']")
            
            if not title_elem:
                continue

            full_url = href if href.startswith("http") else "https://www.wanted.co.kr" + href

            # Experience parsing: Wanted often mixes location and experience in this span
            loc_exp_text = location_elem.get_text(strip=True) if location_elem else None
            location = None
            experience = None
            
            if loc_exp_text:
                if any(x in loc_exp_text for x in ["경력", "신입", "년"]):
                    experience = loc_exp_text
                else:
                    location = loc_exp_text

            jobs.append(
                JobCreate(
                    title=title_elem.get_text(strip=True),
                    company=company_elem.get_text(strip=True) if company_elem else "Unknown",
                    url=full_url,
                    site=JobSite.WANTED,
                    location=location,
                    salary=None,
                    experience=experience,
                )
            )

        return jobs

    async def extract_details(self, url: str) -> dict:
        """
        Fetch details from Wanted job page using the crawler's browser context.
        """
        try:
            # Wait for the top-level main container as described by the user
            html = await self.fetch_page(url, wait_for_selector="main[class*='JobDetail_jobDetail']", timeout=30000)
            soup = BeautifulSoup(html, "html.parser")
            
            # Target the content wrapper or the specific article
            content_area = soup.select_one("div[class*='JobDetail_contentWrapper']") or \
                           soup.select_one("article[class*='JobDescription_JobDescription']") or \
                           soup.select_one("section[class*='JobContent_JobContent']")
            
            description = ""
            if content_area:
                description = content_area.get_text(separator="\n", strip=True)
            else:
                # Last resort fallback to main content
                main_cont = soup.select_one("main")
                description = main_cont.get_text(separator="\n", strip=True) if main_cont else ""
            
            image_url = None
            if content_area:
                img = content_area.select_one("img")
                if img:
                    image_url = img.get("src")

            return {
                "description": description,
                "description_image_url": image_url
            }

        except Exception as e:
            print(f"Error extracting Wanted details: {e}")
            return {"description": None, "description_image_url": None}