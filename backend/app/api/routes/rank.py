import logging
from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime

from app.db.postgres_client import db
from app.models.schemas import RankRequest, RankingResponse
from app.core.ranker import rank_resumes, get_ranking_summary

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rank", tags=["Ranking"])

@router.post("/", response_model=RankingResponse)
async def trigger_ranking(request: RankRequest):
    """
    Ranks multiple resumes against a single JD.
    """
    # 1. Validation
    if len(request.resume_job_ids) < 2:
        raise HTTPException(status_code=400, detail="Ranking requires at least 2 resumes")
    if len(request.resume_job_ids) > 20:
        raise HTTPException(status_code=400, detail="Max 20 resumes allowed per ranking session")
        
    # Check JD exists
    jd = db.get_jd_job(request.jd_job_id)
    if not jd:
        raise HTTPException(status_code=404, detail="Job Description not found")
        
    # Check Resumes exist and are processed
    valid_ids = []
    for rid in request.resume_job_ids:
        job = db.get_resume_job(rid)
        if job and job["status"] == "done":
            valid_ids.append(rid)
        else:
            logger.warning(f"Resume {rid} is missing or not processed. Skipping from ranking.")
            
    if len(valid_ids) < 2:
        raise HTTPException(status_code=400, detail="Not enough valid/processed resumes to perform ranking")

    try:
        # 2. Perform Ranking
        ranked_results = rank_resumes(valid_ids, request.jd_job_id)
        
        # 3. Get Summary
        summary = get_ranking_summary(ranked_results)
        
        # 4. Store in DB
        session_id = db.create_ranking_session(
            jd_job_id=request.jd_job_id,
            resume_job_ids=valid_ids,
            ranked_results=ranked_results
        )
        
        return RankingResponse(
            session_id=session_id,
            jd_job_id=request.jd_job_id,
            summary=summary,
            rankings=ranked_results,
            created_at=datetime.now()
        )
    except Exception as e:
        logger.error(f"Ranking failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}", response_model=RankingResponse)
async def get_ranking_session(session_id: str):
    """
    Fetches a previous ranking session result.
    """
    session = db.get_ranking_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Ranking session not found")
        
    return RankingResponse(
        session_id=str(session["id"]),
        jd_job_id=str(session["jd_job_id"]),
        summary=get_ranking_summary(session["ranked_results"]),
        rankings=session["ranked_results"],
        created_at=session["created_at"]
    )
