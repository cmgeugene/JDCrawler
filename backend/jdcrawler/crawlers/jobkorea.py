from bs4 import BeautifulSoup

from jdcrawler.crawlers.base import BaseCrawler
from jdcrawler.models.job import JobCreate, JobSite


class JobkoreaCrawler(BaseCrawler):
    def __init__(self, headless: bool = True, rate_limit_delay: float = 3.0):
        super().__init__(headless, rate_limit_delay)
        self.base_url = "https://www.jobkorea.co.kr/Search"

    async def crawl(self, keyword: str) -> list[JobCreate]:
        url = f"{self.base_url}?stext={keyword}"
        # New JobKorea uses data-sentry-component="CardJob" for job cards
        html = await self.fetch_page(url, wait_for_selector="div[data-sentry-component='CardJob']")
        return self._parse_jobs(html)

    def _parse_jobs(self, html: str) -> list[JobCreate]:
        soup = BeautifulSoup(html, "html.parser")
        job_cards = soup.select("div[data-sentry-component='CardJob']")
        jobs = []

        for card in job_cards:
            # Title is in a span with a specific variant size class
            title_elem = card.select_one("span[class*='Typography_variant_size18']")
            # Company is in a span with a slightly smaller variant size
            company_elem = card.select_one("span[class*='Typography_variant_size16']")
            # Location often has an icon emoji--basicemoji-place2 next to it
            # Structure: div(GrayChip) -> div -> div(emoji) ... span(text)
            location_elem = None
            place_emoji = card.select_one(".emoji--basicemoji-place2")
            if place_emoji:
                # Find the parent GrayChip
                gray_chip = place_emoji.find_parent("div", attrs={"data-sentry-component": "GrayChip"})
                if gray_chip:
                    location_elem = gray_chip.select_one("span")

            if not location_elem:
                # Fallback for older layouts or if structure changes again
                location_elem = card.select_one("div[class*='GrayChip'] span")

            link_elem = card.select_one("a[href*='/Recruit/GI_Read/']")

            if not title_elem or not company_elem or not link_elem:
                continue

            href = link_elem.get("href", "")
            full_url = (
                href if href.startswith("http") else "https://www.jobkorea.co.kr" + href
            )

            jobs.append(
                JobCreate(
                    title=title_elem.get_text(strip=True),
                    company=company_elem.get_text(strip=True),
                    url=full_url,
                    site=JobSite.JOBKOREA,
                    location=location_elem.get_text(strip=True) if location_elem else None,
                    salary=None,
                )
            )

        return jobs
