import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from app.core.ingestion import parse_file
from app.db.postgres_client import db
from app.chains.jd_analyzer_chain import analyze_jd
from app.core.skill_normalizer import normalize_skills
from app.core.embeddings import store_jd_embedding

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jd", tags=["Job Description"])

@router.post("/upload")
async def upload_jd(
    file: Optional[UploadFile] = File(None),
    jd_text: Optional[str] = Form(None)
):
    """
    Uploads and parses a Job Description. 
    Accepts either a file (PDF/DOCX) or plain text.
    """
    raw_text = ""
    
    if file:
        content = await file.read()
        raw_text = parse_file(content, file.filename)
    elif jd_text:
        raw_text = jd_text
    else:
        raise HTTPException(status_code=400, detail="Either file or jd_text must be provided")
        
    if len(raw_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Job description text is too short")
        
    try:
        # 1. Parse JD using LangChain
        parsed_jd = analyze_jd(raw_text)
        
        # 2. Normalize Skills
        parsed_jd.required_skills = normalize_skills(parsed_jd.required_skills)
        parsed_jd.preferred_skills = normalize_skills(parsed_jd.preferred_skills)
        
        # 3. Store in PostgreSQL
        jd_job_id = db.create_jd_job(raw_text, parsed_jd.model_dump())
        
        # 4. Embed and Store in Qdrant
        store_jd_embedding(jd_job_id, raw_text, {
            "role_title": parsed_jd.role_title,
            "skills_count": len(parsed_jd.required_skills)
        })
        
        return {
            "jd_job_id": jd_job_id,
            "role_title": parsed_jd.role_title,
            "required_skills": parsed_jd.required_skills,
            "preferred_skills": parsed_jd.preferred_skills,
            "min_experience_years": parsed_jd.min_experience_years,
            "status": "parsed"
        }
        
    except Exception as e:
        logger.error(f"JD upload/parse failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
