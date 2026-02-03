from fastapi import APIRouter, Request
from jdcrawler.models.profile import UserProfile, UserProfileUpdate

router = APIRouter(prefix="/api/profile", tags=["profile"])

def get_db(request: Request):
    return request.app.state.db

@router.get("", response_model=UserProfile)
async def get_profile(request: Request):
    db = get_db(request)
    return db.get_profile()

@router.post("", response_model=UserProfile)
async def update_profile(request: Request, data: UserProfileUpdate):
    db = get_db(request)
    return db.update_profile(data)
