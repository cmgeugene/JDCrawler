import asyncio
import json
import httpx
from bs4 import BeautifulSoup

from jdcrawler.crawlers.base import BaseCrawler
from jdcrawler.models.job import JobCreate, JobSite


class WantedCrawler(BaseCrawler):
    def __init__(self, headless: bool = True, rate_limit_delay: float = 3.0):
        super().__init__(headless, rate_limit_delay)
        self.base_url = "https://www.wanted.co.kr/search"

    async def crawl(self, keyword: str) -> list[JobCreate]:
        url = f"{self.base_url}?query={keyword}"
        html = await self.fetch_page(url, wait_for_selector="div[class*='JobCard_container']")
        jobs = self._parse_jobs(html)
        return await self._enrich_locations(jobs)

    def _parse_jobs(self, html: str) -> list[JobCreate]:
        soup = BeautifulSoup(html, "html.parser")
        job_cards = soup.select("div[class*='JobCard_container']")
        jobs = []

        for card in job_cards:
            title_elem = card.select_one("strong[class*='JobCard_title']")
            company_elem = card.select_one("span[class*='CompanyNameWithLocationPeriod_CompanyNameWithLocationPeriod__company']")
            location_elem = card.select_one("span[class*='CompanyNameWithLocationPeriod_CompanyNameWithLocationPeriod__location']")
            link_elem = card.select_one("a[href*='/wd/']")

            if not title_elem or not company_elem or not link_elem:
                continue

            href = link_elem.get("href", "")
            full_url = (
                href if href.startswith("http") else "https://www.wanted.co.kr" + href
            )

            location = location_elem.get_text(strip=True) if location_elem else None
            # Wanted search cards often show experience (e.g. "경력 3-5년") in the class named 'location'
            # If it looks like experience, do not use it as location.
            if location and (any(x in location for x in ["경력", "신입", "년"]) or location[0].isdigit()):
                 location = None

            jobs.append(
                JobCreate(
                    title=title_elem.get_text(strip=True),
                    company=company_elem.get_text(strip=True),
                    url=full_url,
                    site=JobSite.WANTED,
                    location=location,
                    salary=None,
                )
            )

        return jobs

    async def _enrich_locations(self, jobs: list[JobCreate]) -> list[JobCreate]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
            tasks = [self._fetch_location(client, job) for job in jobs]
            return await asyncio.gather(*tasks)

    async def _fetch_location(self, client: httpx.AsyncClient, job: JobCreate) -> JobCreate:
        try:
            # If location is already valid (unlikely given current logic), skip
            if job.location:
                return job

            response = await client.get(job.url)
            if response.status_code != 200:
                return job

            soup = BeautifulSoup(response.text, "html.parser")
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script.string)
                    if data.get("@type") == "JobPosting":
                        address = data.get("jobLocation", {}).get("address", {})
                        region = address.get("addressRegion", "")
                        locality = address.get("addressLocality", "")
                        
                        full_location = f"{region} {locality}".strip()
                        if full_location:
                            job.location = full_location
                            break
                except (json.JSONDecodeError, AttributeError):
                    continue
            
            # Fallback: check meta tags if JSON-LD fails
            if not job.location:
                 meta_desc = soup.find("meta", {"name": "description"})
                 if meta_desc:
                     content = meta_desc.get("content", "")
                     # Example: "회사 위치: 서울 송파구"
                     if "회사 위치:" in content:
                         parts = content.split("회사 위치:")
                         if len(parts) > 1:
                             # Extract text after "회사 위치:" until next newline or comma or simple length
                             loc_part = parts[1].strip().split("\n")[0].split("자격 요건")[0].strip()
                             job.location = loc_part

        except Exception as e:
            # Ignore errors to keep the partial job data
            print(f"Error fetching details for {job.url}: {e}")
        
        return job