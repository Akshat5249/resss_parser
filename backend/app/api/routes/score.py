import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID

from app.db.postgres_client import db
from app.core.scorer import compute_ats_score_baseline, get_score_label
from app.models.schemas import ResumeData, ScoreResponse, ScoreBreakdown

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/score", tags=["Scoring"])

class ScoreRequest(BaseModel):
    resume_job_id: UUID

@router.post("/", response_model=ScoreResponse)
async def get_score(request: ScoreRequest):
    """
    Retrieves the score for a specific resume job. 
    If not in DB, re-computes from stored parsed data.
    """
    job_id = str(request.resume_job_id)
    
    # 1. Fetch job
    job = db.get_resume_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Resume job not found")
    
    if job["status"] != "done":
        raise HTTPException(status_code=400, detail=f"Job is not ready. Status: {job['status']}")
    
    # 2. Fetch analysis result
    analysis = db.get_analysis_result(job_id)
    
    if analysis:
        # Return stored score
        return ScoreResponse(
            job_id=request.resume_job_id,
            score=ScoreBreakdown(**analysis["score_breakdown"]),
            created_at=analysis["created_at"]
        )
    
    # 3. Re-compute if analysis missing but job done
    if not job.get("parsed_data") or not job.get("raw_text"):
        raise HTTPException(status_code=500, detail="Job marked as done but missing data for scoring")
    
    try:
        parsed_data = ResumeData(**job["parsed_data"])
        raw_text = job["raw_text"]
        
        score_breakdown = compute_ats_score_baseline(parsed_data, raw_text)
        
        return ScoreResponse(
            job_id=request.resume_job_id,
            score=score_breakdown,
            created_at=job["updated_at"]
        )
    except Exception as e:
        logger.error(f"Re-computing score failed for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to compute score from stored data")
