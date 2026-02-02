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
            experience = None
            
            # Wanted search cards often show experience (e.g. "경력 3-5년") in the class named 'location' or similar text nodes
            # If the location text looks like experience, treat it as experience.
            if location and (any(x in location for x in ["경력", "신입", "년"]) or (len(location) > 0 and location[0].isdigit())):
                 experience = location
                 location = None # Reset location if it was actually experience

            jobs.append(
                JobCreate(
                    title=title_elem.get_text(strip=True),
                    company=company_elem.get_text(strip=True),
                    url=full_url,
                    site=JobSite.WANTED,
                    location=location,
                    salary=None,
                    experience=experience,
                )
            )

        return jobs

    async def _enrich_locations(self, jobs: list[JobCreate]) -> list[JobCreate]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
            tasks = [self._fetch_details(client, job) for job in jobs]
            return await asyncio.gather(*tasks)

    async def _fetch_details(self, client: httpx.AsyncClient, job: JobCreate) -> JobCreate:
        try:
            # If we have everything, skip
            if job.location and job.experience:
                return job

            response = await client.get(job.url)
            if response.status_code != 200:
                return job

            soup = BeautifulSoup(response.text, "html.parser")
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script.string)
                    if data.get("@type") == "JobPosting":
                        # Location
                        if not job.location:
                            address = data.get("jobLocation", {}).get("address", {})
                            region = address.get("addressRegion", "")
                            locality = address.get("addressLocality", "")
                            full_location = f"{region} {locality}".strip()
                            if full_location:
                                job.location = full_location
                        
                        # Experience (often in requirements or description, but sometimes unstructured)
                        # We can look for "experienceRequirements" if present, or parse description
                        # Wanted specific: "qualifications" text often contains experience
                        
                        # Salary
                        if not job.salary:
                            base_salary = data.get("baseSalary", {})
                            if isinstance(base_salary, dict):
                                value = base_salary.get("value", {})
                                if isinstance(value, dict):
                                    min_sal = value.get("minValue")
                                    max_sal = value.get("maxValue")
                                    unit = value.get("unitText", "KRW")
                                    if min_sal:
                                        job.salary = f"{min_sal} - {max_sal} {unit}"
                        
                        # Deadline
                        if not job.deadline:
                            valid_through = data.get("validThrough")
                            if valid_through:
                                job.deadline = valid_through

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