import logging
from fastapi import APIRouter, HTTPException
from uuid import UUID, uuid4

from app.db.postgres_client import db
from app.workers.tasks import analyze_resume_jd_task
from app.models.schemas import AnalyzeRequest, ScoreBreakdown
from app.core.scorer import get_score_label

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analyze", tags=["Analysis"])

@router.post("/")
async def trigger_analysis(request: AnalyzeRequest):
    """
    Triggers a full JD-aware analysis for a resume.
    """
    resume_job_id = str(request.resume_job_id)
    jd_job_id = str(request.jd_job_id)
    
    if not jd_job_id:
        raise HTTPException(status_code=400, detail="jd_job_id is required for this endpoint")

    # 1. Fetch resume job
    resume_job = db.get_resume_job(resume_job_id)
    if not resume_job:
        raise HTTPException(status_code=404, detail="Resume job not found")
    
    if resume_job["status"] != "done":
        raise HTTPException(status_code=400, detail=f"Resume not processed yet. Status: {resume_job['status']}")
        
    # 2. Fetch JD job
    jd_job = db.get_jd_job(jd_job_id)
    if not jd_job:
        raise HTTPException(status_code=404, detail="Job description not found")
        
    # 3. Enqueue Celery task
    analyze_resume_jd_task.delay(resume_job_id, jd_job_id)
    
    return {
        "analysis_id": str(uuid4()), # Temporary ID, actual one generated in DB
        "resume_job_id": resume_job_id,
        "jd_job_id": jd_job_id,
        "status": "processing",
        "message": "JD analysis started. Poll /analyze/{resume_job_id}/status for updates."
    }

@router.get("/{resume_job_id}/status")
async def get_analysis_status(resume_job_id: UUID):
    """
    Returns the status of the most recent JD-aware analysis.
    """
    result = db.get_analysis_result(str(resume_job_id))
    
    # If no result at all, it's definitely not found
    if not result:
        return {"status": "not_found", "message": "No analysis found for this resume. Upload and process a resume first."}
        
    # If jd_job_id is null, it's the baseline score from Phase 1
    if not result.get("jd_job_id"):
        # Check if the resume itself is still processing
        resume_job = db.get_resume_job(str(resume_job_id))
        if resume_job and resume_job["status"] != "done":
             return {"status": "processing", "message": "Resume parsing in progress..."}
        
        return {"status": "baseline_ready", "message": "Baseline analysis complete. JD-aware matching is pending or not started."}

    return {
        "status": "done",
        "message": "JD-aware analysis complete!",
        "score_total": result["score_total"]
    }

@router.get("/{resume_job_id}")
async def get_analysis_results(resume_job_id: UUID):
    """
    Returns full analysis results for a resume vs JD match.
    """
    result = db.get_analysis_result(str(resume_job_id))
    if not result or not result.get("jd_job_id"):
        raise HTTPException(status_code=404, detail="JD-aware analysis result not found")
    
    jd_job = db.get_jd_job(str(result["jd_job_id"]))
    
    return {
        "resume_job_id": resume_job_id,
        "jd_job_id": result["jd_job_id"],
        "score": result["score_breakdown"],
        "matched_skills": result["matched_skills"],
        "semantic_similarity": result["semantic_similarity"],
        "gaps": result["gaps"],
        "score_label": get_score_label(result["score_total"]),
        "created_at": result["created_at"]
    }
