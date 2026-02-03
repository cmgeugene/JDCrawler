from bs4 import BeautifulSoup

from jdcrawler.crawlers.base import BaseCrawler
from jdcrawler.models.job import JobCreate, JobSite


class SaraminCrawler(BaseCrawler):
    def __init__(self, headless: bool = True, rate_limit_delay: float = 3.0, **kwargs):
        super().__init__(headless, rate_limit_delay, **kwargs)
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
            
            location = None
            experience = None
            salary = None

            # Saramin usually follows: Location | Experience | Education | Type | Salary (optional)
            # We iterate to find them by keywords or position
            for span in condition_spans:
                text = span.get_text(strip=True)
                if not location and ("서울" in text or "경기" in text or "인천" in text or "부산" in text or "대구" in text or "광주" in text or "대전" in text or "울산" in text or "세종" in text or "강원" in text or "충북" in text or "충남" in text or "전북" in text or "전남" in text or "경북" in text or "경남" in text or "제주" in text or "전국" in text):
                    location = text
                elif not experience and ("신입" in text or "경력" in text or "무관" in text):
                    experience = text
                elif "만원" in text or "연봉" in text:
                    salary = text
            
            # Fallback: if location wasn't found by keyword, take the first one
            if not location and condition_spans:
                 location = condition_spans[0].get_text(strip=True)

            # Deadline extraction
            deadline_elem = card.select_one(".job_date .date")
            deadline = deadline_elem.get_text(strip=True) if deadline_elem else None

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
                    experience=experience,
                    deadline=deadline,
                )
            )

        return jobs

    async def extract_details(self, url: str) -> dict:
        """
        Fetch details from the job page.
        """
        try:
            # Using fetch_page from base class
            html = await self.fetch_page(url, wait_until="domcontentloaded")
            soup = BeautifulSoup(html, "html.parser")
            
            # JD text often in .user_content, .wrap_jv_cont, or #recruit_info
            # Some jobs use iframe, which is harder to crawl with simple fetch.
            # We try common selectors first.
            jd_elem = soup.select_one(".user_content") or soup.select_one("#recruit_info") or soup.select_one(".wrap_jv_cont")
            
            description = ""
            image_url = None
            
            if jd_elem:
                # 1. Try to get text
                description = jd_elem.get_text(separator="\n", strip=True)
                
                # 2. Design for images: check for large images in the JD area
                images = jd_elem.select("img")
                for img in images:
                    src = img.get("src", "")
                    # Look for likely JD images (often large or in specific paths)
                    if src and any(ext in src.lower() for ext in [".jpg", ".png", ".jpeg", ".gif"]):
                        # Just take the first substantial-looking image as a candidate
                        if "http" in src:
                            image_url = src
                            break
            
            # If description is very short, it's likely an image-only job
            if len(description) < 200:
                # Keep looking for images if not found
                if not image_url:
                    all_imgs = soup.select("img")
                    # Heuristic for JD images
                    for img in all_imgs:
                         alt = img.get("alt", "")
                         if "공고" in alt or "상세" in alt:
                             image_url = img.get("src")
                             break

            return {
                "description": description,
                "description_image_url": image_url
            }
        except Exception as e:
            print(f"Error extracting Saramin details: {e}")
            return {"description": None, "description_image_url": None}
