import logging
import json
from fastapi import APIRouter, HTTPException
from uuid import UUID, uuid4

from app.db.postgres_client import db
from app.workers.tasks import analyze_resume_jd_task
from app.models.schemas import AnalyzeRequest
from app.core.scorer import get_score_label

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analyze", tags=["Analysis"])

@router.post("/")
async def trigger_analysis(request: AnalyzeRequest):
    """
    Triggers a full JD-aware analysis for a resume (Phase 3).
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
    # Ensure we use the correct task name as defined in tasks.py
    analyze_resume_jd_task.delay(resume_job_id, jd_job_id)
    
    return {
        "analysis_id": str(uuid4()), 
        "resume_job_id": resume_job_id,
        "jd_job_id": jd_job_id,
        "status": "processing",
        "message": "Full Phase 3 analysis started. Poll /analyze/{resume_job_id}/status for updates."
    }

@router.get("/{resume_job_id}/status")
async def get_analysis_status(resume_job_id: UUID):
    """
    Returns the status of the most recent JD-aware analysis.
    """
    result = db.get_analysis_result(str(resume_job_id))
    
    if not result:
        return {"status": "not_found", "message": "No analysis found for this resume."}
        
    if not result.get("jd_job_id"):
        resume_job = db.get_resume_job(str(resume_job_id))
        if resume_job and resume_job["status"] != "done":
             return {"status": "processing", "message": "Resume parsing in progress..."}
        
        return {"status": "baseline_ready", "message": "Only baseline analysis available. POST to /analyze for full matching."}

    return {
        "status": "done",
        "message": "Full Phase 3 analysis complete!",
        "score_total": result["score_total"]
    }

@router.get("/{resume_job_id}")
async def get_analysis_results(resume_job_id: UUID):
    """
    Returns the complete Phase 3 analysis results.
    """
    result = db.get_analysis_result(str(resume_job_id))
    if not result or not result.get("jd_job_id"):
        raise HTTPException(status_code=404, detail="JD-aware analysis result not found")
    
    # BACKEND: Add role_title to analyze response
    role_title = ""
    jd_job_id = result.get("jd_job_id")
    if jd_job_id:
        jd_job = db.get_jd_job(str(jd_job_id))
        if jd_job:
            jd_parsed_data = jd_job.get("parsed_data") or {}
            if isinstance(jd_parsed_data, str):
                try:
                    jd_parsed_data = json.loads(jd_parsed_data)
                except:
                    jd_parsed_data = {}
            role_title = jd_parsed_data.get("role_title", "")

    return {
        "resume_job_id": str(resume_job_id),
        "jd_job_id": str(jd_job_id),
        "role_title": role_title,
        "score": result["score_breakdown"],
        "score_label": get_score_label(result["score_total"]),
        "semantic_similarity": result["semantic_similarity"],
        "matched_skills": result["matched_skills"],
        "gaps": result.get("gaps"),
        "enhancements": result.get("enhancements", []),
        "formatting": result.get("compliance_issues"),
        "learning_path": result.get("learning_path"),
        "feedback": result.get("feedback_text"),
        "created_at": result["created_at"]
    }
