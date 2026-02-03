from abc import ABC, abstractmethod

from playwright.async_api import Browser, async_playwright

from jdcrawler.utils.rate_limiter import RateLimiter
from jdcrawler.utils.retry import retry
from jdcrawler.models.job import JobCreate


class BaseCrawler(ABC):
    def __init__(
        self,
        headless: bool = True,
        rate_limit_delay: float = 3.0,
        jitter: float = 2.0,
    ):
        self.headless = headless
        self.rate_limiter = RateLimiter(delay=rate_limit_delay, jitter=jitter)
        self.browser: Browser | None = None
        self.playwright = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-infobars",
                "--window-position=0,0",
                "--ignore-certificate-errors",
            ]
        )
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}, # Fixed large viewport
            device_scale_factor=1,
            locale="ko-KR",
            timezone_id="Asia/Seoul",
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    @abstractmethod
    async def crawl(self, keyword: str) -> list["JobCreate"]:
        pass

    @retry(max_attempts=3, delay=2.0)
    async def fetch_page(
        self,
        url: str,
        timeout: float = 90000,
        wait_until: str = "domcontentloaded",
        wait_for_selector: str | None = None,
    ):
        await self.rate_limiter.acquire()
        page = await self.context.new_page()
        try:
            await page.goto(url, timeout=timeout, wait_until=wait_until)
            
            if wait_for_selector:
                try:
                    await page.wait_for_selector(wait_for_selector, timeout=timeout)
                except Exception as e:
                    print(f"Warning: Timeout waiting for selector '{wait_for_selector}' on {url}")

            # Fallback/General wait if no specific selector or just to be safe
            if not wait_for_selector:
                 try:
                    await page.wait_for_selector("body", timeout=timeout)
                 except:
                    pass

            content = await page.content()
        finally:
            await page.close()
        return content
