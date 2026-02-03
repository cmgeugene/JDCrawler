from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


def get_db(request: Request):
    return request.app.state.db


@router.get("/new-jobs-count")
def get_new_jobs_count(request: Request):
    db = get_db(request)
    count = db.get_new_jobs_count()
    return {"count": count}


@router.post("/mark-read")
def mark_read(request: Request):
    db = get_db(request)
    db.mark_read()
    return {"status": "ok"}