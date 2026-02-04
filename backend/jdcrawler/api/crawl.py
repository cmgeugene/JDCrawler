from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from pydantic import BaseModel, field_validator

from jdcrawler.services.crawler import CrawlerService

router = APIRouter(prefix="/api/crawl", tags=["crawl"])


class CrawlRequest(BaseModel):
    site: str
    keyword: str

    @field_validator("site")
    @classmethod
    def site_must_be_valid(cls, v: str) -> str:
        if v not in ["saramin", "jobkorea", "wanted"]:
            raise ValueError("Invalid site")
        return v


class CrawlResponse(BaseModel):
    status: str
    site: str
    keyword: str
    jobs_crawled: int
    message: str


def get_db(request: Request):
    return request.app.state.db


import os

@router.post("")
async def crawl_site(request: CrawlRequest, http_request: Request):
    db = get_db(http_request)
    service = CrawlerService(db)

    import traceback
    try:
        headless = os.getenv("HEADLESS", "true").lower() == "true"
        jobs_crawled = await service.crawl_keyword(request.keyword, sites=[request.site], headless=headless)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    return CrawlResponse(
        status="completed",
        site=request.site,
        keyword=request.keyword,
        jobs_crawled=jobs_crawled,
        message=f"Successfully crawled {jobs_crawled} jobs from {request.site}",
    )


@router.post("/all")
async def crawl_all(http_request: Request, background_tasks: BackgroundTasks):
    """
    Trigger crawling for all active keywords in the background.
    """
    db = get_db(http_request)
    
    async def _run_crawl():
        service = CrawlerService(db)
        headless = os.getenv("HEADLESS", "true").lower() == "true"
        await service.crawl_all_active_keywords(headless=headless)

    background_tasks.add_task(_run_crawl)
    
    return {"status": "accepted", "message": "Crawling started in background"}


@router.get("/status")
def get_crawl_status():
    from jdcrawler.scheduler import scheduler
    jobs = scheduler.get_jobs()
    
    return {
        "status": "running" if scheduler.running else "stopped",
        "jobs": [{"id": j.id, "next_run_time": j.next_run_time} for j in jobs],
    }
