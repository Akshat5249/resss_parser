from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jd", tags=["Job Description"])

@router.post("/upload")
async def upload_jd(
    jd_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    """
    Upload a job description either as text or as a PDF/DOCX file.
    At least one of jd_text or file must be provided.
    """
    logger.info(f"JD upload called. jd_text length: {len(jd_text) if jd_text else 0}, file: {file.filename if file else None}")
    
    raw_text = None
    
    # Case 1: text provided directly
    if jd_text and jd_text.strip():
        raw_text = jd_text.strip()
        logger.info(f"Using provided JD text, length: {len(raw_text)}")
    
    # Case 2: file provided
    elif file and file.filename:
        logger.info(f"Parsing JD from file: {file.filename}")
        try:
            content = await file.read()
            from app.core.ingestion import parse_file
            raw_text = parse_file(content, file.filename)
            logger.info(f"JD file parsed, text length: {len(raw_text)}")
        except Exception as e:
            logger.error(f"Failed to parse JD file: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse JD file: {str(e)}"
            )
    
    # Case 3: neither provided
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide either jd_text or a file upload"
        )
    
    # Validate minimum length
    if len(raw_text) < 50:
        raise HTTPException(
            status_code=400,
            detail=f"JD text too short ({len(raw_text)} chars). Add more detail."
        )
    
    # Parse JD with LangChain
    logger.info("Starting JD LangChain parsing...")
    try:
        from app.chains.jd_analyzer_chain import analyze_jd
        parsed_jd = analyze_jd(raw_text)
        logger.info(f"JD parsed successfully. Role: {parsed_jd.role_title}, Required skills: {len(parsed_jd.required_skills)}")
    except Exception as e:
        logger.error(f"JD parsing chain failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse job description: {str(e)}"
        )
    
    # Normalize skills
    try:
        from app.core.skill_normalizer import normalize_skills
        parsed_jd.required_skills = normalize_skills(parsed_jd.required_skills)
        parsed_jd.preferred_skills = normalize_skills(parsed_jd.preferred_skills)
    except Exception as e:
        logger.warning(f"Skill normalization failed (non-fatal): {e}")
    
    # Store in database
    logger.info("Storing JD in database...")
    try:
        from app.db.postgres_client import db
        jd_job_id = db.create_jd_job(
            raw_text=raw_text,
            parsed_data=parsed_jd.model_dump()
        )
        logger.info(f"JD stored with id: {jd_job_id}")
    except Exception as e:
        logger.error(f"Database insert failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store job description: {str(e)}"
        )
    
    # Store embedding in Qdrant (non-fatal if fails)
    try:
        from app.core.embeddings import store_jd_embedding
        store_jd_embedding(jd_job_id, raw_text, {
            "role_title": parsed_jd.role_title
        })
        logger.info(f"JD embedding stored in Qdrant")
    except Exception as e:
        logger.warning(f"Qdrant embedding failed (non-fatal): {e}")
    
    return {
        "jd_job_id": jd_job_id,
        "role_title": parsed_jd.role_title,
        "required_skills": parsed_jd.required_skills,
        "preferred_skills": parsed_jd.preferred_skills,
        "min_experience_years": parsed_jd.min_experience_years,
        "status": "parsed"
    }
