from fastapi import APIRouter, Query
from ai.recommender import recommend_next

router = APIRouter()

@router.get("/suggest")
def suggest_next(level: str = Query("중")):
    return {"level": level, "suggestion": recommend_next(level)}
