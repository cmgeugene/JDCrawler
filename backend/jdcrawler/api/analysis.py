from fastapi import APIRouter, Request, HTTPException
from jdcrawler.services.analysis import AnalysisService
from jdcrawler.db.schema import JobTable
from sqlalchemy import update

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

def get_db(request: Request):
    return request.app.state.db

@router.post("/{job_id}")
async def analyze_job(job_id: int, request: Request):
    db = get_db(request)
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.description:
        raise HTTPException(status_code=400, detail="Job description is required for AI analysis")

    profile = db.get_profile()
    analysis_service = AnalysisService()
    
    # Perform AI Analysis
    result = await analysis_service.analyze_job_suitability(job, profile)
    
    # Update DB with AI results
    stmt = (
        update(JobTable)
        .where(JobTable.id == job_id)
        .values(
            ai_score=result["score"],
            ai_summary=result["summary"],
            ai_status=result["status"]
        )
    )
    db.jobs_session.execute(stmt)
    db.jobs_session.commit()
    
    return result