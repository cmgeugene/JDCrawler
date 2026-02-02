from bs4 import BeautifulSoup

from jdcrawler.crawlers.base import BaseCrawler
from jdcrawler.models.job import JobCreate, JobSite


class SaraminCrawler(BaseCrawler):
    def __init__(self, headless: bool = True, rate_limit_delay: float = 3.0):
        super().__init__(headless, rate_limit_delay)
        self.base_url = "https://www.saramin.co.kr/zf_user/search"

    async def crawl(self, keyword: str) -> list[JobCreate]:
        url = f"{self.base_url}?searchword={keyword}"
        html = await self.fetch_page(url, wait_for_selector="div.item_recruit")
        return self._parse_jobs(html)

    def _parse_jobs(self, html: str) -> list[JobCreate]:
        soup = BeautifulSoup(html, "html.parser")
        job_cards = soup.select("div.item_recruit")
        jobs = []

        for card in job_cards:
            title_elem = card.select_one(".job_tit a")
            company_elem = card.select_one(".corp_name a")
            
            # Location is usually the first span in job_condition
            condition_spans = card.select(".job_condition span")
            location = condition_spans[0].get_text(strip=True) if condition_spans else None
            
            # Salary search in conditions
            salary = None
            for span in condition_spans:
                text = span.get_text(strip=True)
                if "만원" in text or "연봉" in text:
                    salary = text
                    break

            if not title_elem or not company_elem:
                continue

            href = title_elem.get("href", "")
            full_url = (
                href if href.startswith("http") else "https://www.saramin.co.kr" + href
            )

            jobs.append(
                JobCreate(
                    title=title_elem.get_text(strip=True),
                    company=company_elem.get_text(strip=True),
                    url=full_url,
                    site=JobSite.SARAMIN,
                    location=location,
                    salary=salary,
                )
            )

        return jobs
