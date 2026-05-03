import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import Optional
from uuid import UUID

from app.core.ingestion import validate_file, parse_file, clean_text
from app.db.postgres_client import db
from app.chains.resume_parser_chain import parse_resume
from app.core.skill_normalizer import normalize_skills
from app.core.scorer import compute_ats_score_baseline, get_score_label
from app.models.schemas import UploadResumeResponse, ResumeData, ScoreBreakdown

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/resume", tags=["Resume"])

@router.post("/upload", response_model=UploadResumeResponse)
async def upload_resume(file: UploadFile = File(...)):
    """
    Complete pipeline for Resume Upload → Extraction → Parsing → Scoring → Storage.
    Note: Currently synchronous as per Phase 1 requirements.
    """
    content = await file.read()
    filename = file.filename
    
    # 1. Validate file
    validate_file(filename, content)
    
    # 2. Create job in DB
    job_id = db.create_resume_job(filename)
    
    try:
        # 3. Extract and Clean Text
        raw_text = parse_file(content, filename)
        cleaned_text = clean_text(raw_text)
        
        # Update job with raw text
        db.update_resume_job(job_id, raw_text=cleaned_text, status='processing')
        
        # 4. Parse Resume with LangChain
        parsed_data = parse_resume(cleaned_text)
        
        # 5. Normalize Skills
        parsed_data.skills = normalize_skills(parsed_data.skills)
        
        # 6. Compute Baseline Score
        score_breakdown = compute_ats_score_baseline(parsed_data, cleaned_text)
        score_label = get_score_label(score_breakdown.total)
        
        # 7. Update Job as Done
        db.update_resume_job(job_id, parsed_data=parsed_data.model_dump(), status='done')
        
        # 8. Store Analysis Result
        db.create_analysis_result(
            resume_job_id=job_id,
            jd_job_id=None, # Baseline mode
            score_total=int(score_breakdown.total),
            score_breakdown=score_breakdown.model_dump(),
            gaps={"missing_skills": [], "weak_bullets": []} # No gaps in baseline mode
        )
        
        return UploadResumeResponse(
            job_id=UUID(job_id),
            filename=filename,
            status="done",
            char_count=len(cleaned_text),
            parsed_data=parsed_data,
            score=score_breakdown,
            score_label=score_label
        )
        
    except Exception as e:
        logger.error(f"Pipeline failed for job {job_id}: {e}")
        db.update_resume_job(job_id, status='failed', error_message=str(e))
        return UploadResumeResponse(
            job_id=UUID(job_id),
            filename=filename,
            status="failed",
            char_count=0
        )

@router.get("/{job_id}")
async def get_resume(job_id: UUID):
    """
    Fetches resume job details and its analysis result.
    """
    job = db.get_resume_job(str(job_id))
    if not job:
        raise HTTPException(status_code=404, detail="Resume job not found")
    
    analysis = db.get_analysis_result(str(job_id))
    
    # Format response
    response = {
        "job_details": job,
        "analysis": analysis
    }
    
    if analysis:
        response["score_label"] = get_score_label(analysis["score_total"])
        
    return response
