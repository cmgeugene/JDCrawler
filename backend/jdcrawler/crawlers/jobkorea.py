from bs4 import BeautifulSoup

from jdcrawler.crawlers.base import BaseCrawler
from jdcrawler.models.job import JobCreate, JobSite


class JobkoreaCrawler(BaseCrawler):
    def __init__(self, headless: bool = True, rate_limit_delay: float = 3.0, **kwargs):
        super().__init__(headless, rate_limit_delay, **kwargs)
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

            # Experience parsing
            # JobKorea usually has options in a list-like structure in spans
            experience = None
            salary = None
            
            # Try to find experience in option tags
            option_spans = card.select(".option span")
            for span in option_spans:
                text = span.get_text(strip=True)
                if "신입" in text or "경력" in text or "무관" in text:
                    experience = text
                elif "만원" in text or "연봉" in text:
                    salary = text
            
            # Deadline parsing
            deadline_elem = card.select_one(".deadlines")
            if not deadline_elem:
                deadline_elem = card.select_one(".date")
            
            deadline = deadline_elem.get_text(strip=True) if deadline_elem else None

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
                    salary=salary,
                    experience=experience,
                    deadline=deadline,
                )
            )

        return jobs

    async def extract_details(self, url: str) -> dict:
        try:
            # JobKorea can be slow, wait for any significant element or the iframe itself
            html = await self.fetch_page(url, wait_for_selector="body", timeout=30000)
            soup = BeautifulSoup(html, "html.parser")
            
            description = ""
            image_url = None
            
            # 1. Target the specific iframe identified by the user
            # Pattern: /Recruit/GI_Read_Comt_Ifrm or Title: 상세 모집 요강
            iframe = soup.select_one("iframe[src*='GI_Read_Comt_Ifrm']") or \
                     soup.select_one("iframe[title='상세 모집 요강']") or \
                     soup.select_one("#gib_frame")
            
            if iframe:
                iframe_src = iframe.get("src")
                if iframe_src:
                    if not iframe_src.startswith("http"):
                        iframe_src = "https://www.jobkorea.co.kr" + iframe_src
                    
                    # Fetch the iframe content
                    # We use networkidle to ensure content inside iframe document is loaded
                    iframe_html = await self.fetch_page(iframe_src, wait_until="networkidle")
                    iframe_soup = BeautifulSoup(iframe_html, "html.parser")
                    description = iframe_soup.get_text(separator="\n", strip=True)
                    
                    # Image extraction from within iframe
                    img = iframe_soup.select_one("img")
                    if img:
                        image_url = img.get("src")
            
            # 2. Fallback to common content areas if iframe fails or is empty
            if not description or len(description) < 100:
                jd_elem = soup.select_one(".job-view-body") or soup.select_one(".cont") or \
                          soup.select_one(".recruit-info") or soup.select_one(".detail-content")
                
                if jd_elem:
                    description = jd_elem.get_text(separator="\n", strip=True)
                    if not image_url:
                        img = jd_elem.select_one("img")
                        if img:
                            image_url = img.get("src")

            return {
                "description": description,
                "description_image_url": image_url
            }
        except Exception as e:
            print(f"Error extracting JobKorea details: {e}")
            return {"description": None, "description_image_url": None}
