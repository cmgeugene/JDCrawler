from datetime import datetime

from fastapi import APIRouter, Request
from sqlalchemy import select

from jdcrawler.db.schema import JobTable, NotificationTable

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


def get_db(request: Request):
    return request.app.state.db


@router.get("/new-jobs-count")
def get_new_jobs_count(request: Request):
    db = get_db(request)
    session = db.session

    notification = session.execute(select(NotificationTable)).scalar_one_or_none()
    if not notification:
        notification = NotificationTable(last_checked_at=datetime(1970, 1, 1))
        session.add(notification)
        session.commit()
        session.refresh(notification)

    count = (
        session.query(JobTable)
        .filter(JobTable.created_at > notification.last_checked_at)
        .count()
    )
    return {"count": count}


@router.post("/mark-read")
def mark_read(request: Request):
    db = get_db(request)
    session = db.session

    notification = session.execute(select(NotificationTable)).scalar_one_or_none()
    if not notification:
        notification = NotificationTable(last_checked_at=datetime.now())
        session.add(notification)
    else:
        notification.last_checked_at = datetime.now()

    session.commit()
    return {"status": "ok"}
