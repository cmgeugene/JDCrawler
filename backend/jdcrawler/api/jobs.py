from fastapi import APIRouter, HTTPException, Request

from jdcrawler.models.job import JobResponse

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


def get_db(request: Request):
    return request.app.state.db


@router.get("", response_model=list[JobResponse])
def get_jobs(
    request: Request,
    q: str | None = None,
    site: str | None = None,
    bookmarked: bool | None = None,
    limit: int = 100,
    offset: int = 0,
):
    db = get_db(request)
    jobs = db.get_jobs(
        search=q, site=site, bookmarked=bookmarked, limit=limit, offset=offset
    )
    return jobs


@router.get("/stats")
def get_job_stats(request: Request):
    db = get_db(request)
    return db.get_job_stats()


@router.get("/{job_id}", response_model=JobResponse)
def get_job(request: Request, job_id: int):
    db = get_db(request)
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.patch("/{job_id}/bookmark", response_model=JobResponse)
def toggle_bookmark(request: Request, job_id: int):
    db = get_db(request)
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return db.toggle_bookmark(job_id)


@router.patch("/{job_id}/hidden", response_model=JobResponse)
def toggle_hidden(request: Request, job_id: int):
    db = get_db(request)
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return db.toggle_hidden(job_id)
