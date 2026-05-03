from fastapi import APIRouter

router = APIRouter(prefix="/rank", tags=["Ranking"])

@router.post("/")
async def rank_resumes():
    return {"message": "Rank resumes endpoint"}
