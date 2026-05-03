from fastapi import APIRouter

router = APIRouter(prefix="/jd", tags=["Job Description"])

@router.post("/upload")
async def upload_jd():
    return {"message": "Upload JD endpoint"}
