import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
from uuid import UUID

from app.core.ingestion import validate_file, parse_file
from app.db.postgres_client import db
from app.workers.tasks import process_resume_task
from app.models.schemas import UploadResumeResponse
from app.core.scorer import get_score_label

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/resume", tags=["Resume"])

@router.post("/upload", response_model=UploadResumeResponse)
async def upload_resume(file: UploadFile = File(...)):
    """
    Async pipeline for Resume Upload. 
    Returns instantly with job_id and task_id.
    """
    filename = file.filename
    content = await file.read()
    
    # 1. Validate file
    validate_file(filename, content)
    
    try:
        # 2. Extract Text (Fast operation, keep in route)
        raw_text = parse_file(content, filename)
        
        # 3. Create job in DB with status pending
        job_id = db.create_resume_job(filename=filename)
        db.update_resume_job(job_id, raw_text=raw_text, status="pending")
        
        # 4. Trigger Celery task
        task = process_resume_task.delay(job_id)
        
        # 5. Store celery task id
        db.update_resume_job(job_id, celery_task_id=task.id)
        
        return UploadResumeResponse(
            job_id=UUID(job_id),
            task_id=task.id,
            filename=filename,
            status="pending",
            char_count=len(raw_text),
            message="Resume received. Poll /resume/{job_id}/status for updates."
        )
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{job_id}/status")
async def get_resume_status(job_id: UUID):
    """
    Check the current status of a resume processing job.
    """
    job = db.get_resume_job(str(job_id))
    if not job:
        raise HTTPException(status_code=404, detail="Resume job not found")
    
    status = job["status"]
    score_total = None
    
    messages = {
        "pending": "Waiting in queue...",
        "processing": "Analyzing your resume with AI...",
        "done": "Analysis complete!",
        "failed": f"Processing failed: {job.get('error_message')}"
    }
    
    if status == "done":
        analysis = db.get_analysis_result(str(job_id))
        if analysis:
            score_total = analysis["score_total"]
            
    return {
        "job_id": job_id,
        "status": status,
        "message": messages.get(status, "Unknown status"),
        "score_total": score_total
    }

@router.get("/{job_id}")
async def get_resume(job_id: UUID):
    """
    Fetches resume job details and its analysis result.
    """
    job = db.get_resume_job(str(job_id))
    if not job:
        raise HTTPException(status_code=404, detail="Resume job not found")
    
    analysis = db.get_analysis_result(str(job_id))
    
    response = {
        "job_details": job,
        "analysis": analysis
    }
    
    if analysis:
        response["score_label"] = get_score_label(analysis["score_total"])
        
    return response
