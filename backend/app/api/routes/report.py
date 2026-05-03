import logging
import io
import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from uuid import UUID

from app.db.postgres_client import db
from app.core.pdf_generator import generate_ats_report
from app.core.scorer import get_score_label

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/report", tags=["Report"])

@router.get("/{resume_job_id}")
async def get_report(resume_job_id: UUID):
    """
    Generates and returns the ATS report PDF.
    """
    # 1. Fetch analysis result
    result = db.get_analysis_result(str(resume_job_id))
    if not result:
        raise HTTPException(status_code=404, detail="No analysis found for this resume")
    
    # 2. Fetch Job Details
    resume_job = db.get_resume_job(str(resume_job_id))
    if not resume_job:
        raise HTTPException(status_code=404, detail="Resume job not found")
        
    candidate_name = "Candidate"
    if resume_job.get("parsed_data"):
        candidate_name = resume_job["parsed_data"].get("name", "Candidate")
        
    role_title = "Unknown Role"
    if result.get("jd_job_id"):
        jd_job = db.get_jd_job(str(result["jd_job_id"]))
        if jd_job and jd_job.get("parsed_data"):
            role_title = jd_job["parsed_data"].get("role_title", "Specified Role")

    # 3. Build analysis_data dict
    analysis_data = {
        "candidate_name": candidate_name,
        "role_title": role_title,
        "score": result["score_breakdown"],
        "score_label": get_score_label(result["score_total"]),
        "matched_skills": result["matched_skills"],
        "semantic_similarity": result["semantic_similarity"],
        "gaps": result.get("gaps"),
        "enhancements": result.get("enhancements", []),
        "formatting": result.get("compliance_issues"),
        "learning_path": result.get("learning_path"),
        "feedback": result.get("feedback_text")
    }

    try:
        # 4. Generate PDF
        pdf_bytes = generate_ats_report(analysis_data)
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="ATS_Report_{candidate_name.replace(" ", "_")}.pdf"'
            }
        )
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF report")

@router.post("/{resume_job_id}/store")
async def store_report(resume_job_id: UUID):
    """
    Generates report and stores it locally (for now).
    """
    # Reuse logic for simplicity
    response = await get_report(resume_job_id)
    if not isinstance(response, StreamingResponse):
        return response
        
    pdf_bytes = response.body_iterator.__next__() # This is simplified, actual body retrieval varies
    # In FastAPI body is usually consumed. For local store, we just re-run.
    
    # Proper re-run for storage
    result = db.get_analysis_result(str(resume_job_id))
    resume_job = db.get_resume_job(str(resume_job_id))
    
    candidate_name = resume_job["parsed_data"].get("name", "Candidate") if resume_job.get("parsed_data") else "Candidate"
    role_title = "Role"
    if result.get("jd_job_id"):
        jd_job = db.get_jd_job(str(result["jd_job_id"]))
        role_title = jd_job["parsed_data"].get("role_title", "Role") if jd_job else "Role"
        
    analysis_data = {
        "candidate_name": candidate_name,
        "role_title": role_title,
        "score": result["score_breakdown"],
        "score_label": get_score_label(result["score_total"]),
        "matched_skills": result["matched_skills"],
        "gaps": result.get("gaps"),
        "enhancements": result.get("enhancements", []),
        "formatting": result.get("compliance_issues"),
        "learning_path": result.get("learning_path"),
        "feedback": result.get("feedback_text")
    }
    
    pdf_bytes = generate_ats_report(analysis_data)
    
    file_path = f"/tmp/report_{resume_job_id}.pdf"
    with open(file_path, "wb") as f:
        f.write(pdf_bytes)
        
    # Update DB
    db.update_resume_job(str(resume_job_id), file_url=file_path) # Overloading file_url for now
    
    return {"pdf_url": file_path, "message": "Report generated and stored locally in /tmp"}
