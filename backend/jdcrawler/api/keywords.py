from fastapi import APIRouter, HTTPException, Request, Response, status

from jdcrawler.models.keyword import Keyword, KeywordCreate

router = APIRouter(prefix="/api/keywords", tags=["keywords"])


def get_db(request: Request):
    return request.app.state.db


@router.get("", response_model=list[Keyword])
def get_keywords(request: Request):
    db = get_db(request)
    return db.get_keywords()


@router.post("", response_model=Keyword, status_code=status.HTTP_201_CREATED)
def create_keyword(request: Request, keyword_data: KeywordCreate):
    db = get_db(request)
    return db.create_keyword(keyword_data.keyword)


@router.delete("/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_keyword(request: Request, keyword_id: int):
    db = get_db(request)
    keywords = db.get_keywords()
    if not any(k.id == keyword_id for k in keywords):
        raise HTTPException(status_code=404, detail="Keyword not found")
    db.delete_keyword(keyword_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
