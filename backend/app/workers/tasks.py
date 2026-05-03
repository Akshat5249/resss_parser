import logging
from app.workers.celery_app import celery_app
from app.db.postgres_client import db
from app.chains.resume_parser_chain import parse_resume
from app.core.skill_normalizer import normalize_skills
from app.core.scorer import compute_ats_score_baseline, compute_ats_score_with_jd, get_matched_skills, get_score_label
from app.models.schemas import ResumeData, JDData
from app.core.embeddings import compute_similarity, store_resume_embedding, store_jd_embedding

# Phase 3 Imports
from app.core.gap_detector import detect_gaps
from app.chains.enhancement_chain import enhance_weak_bullets
from app.core.formatter_checker import check_formatting
from app.core.learning_path import generate_learning_path
from app.chains.explainability_chain import generate_feedback

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def process_resume_task(self, job_id: str):
    """
    Background task to process a resume: parse, normalize, and score.
    """
    logger.info(f"[{job_id}] Task started")
    try:
        # 1. Update status to processing
        db.update_resume_job(job_id, status="processing")
        
        # 2. Get raw text from DB
        resume_job = db.get_resume_job(job_id)
        if not resume_job:
            raise ValueError(f"Job {job_id} not found in database")
            
        raw_text = resume_job.get("raw_text")
        if not raw_text:
            raise ValueError(f"[{job_id}] Raw text is empty")

        # 3. Start parsing
        logger.info(f"[{job_id}] Starting LangChain parsing")
        parsed_data = parse_resume(raw_text)
        
        # 4. Normalize skills
        logger.info(f"[{job_id}] Parsing complete. Skills count: {len(parsed_data.skills)}")
        parsed_data.skills = normalize_skills(parsed_data.skills)
        
        # 5. Compute score
        score = compute_ats_score_baseline(parsed_data, raw_text)
        logger.info(f"[{job_id}] Score computed: {score.total}")
        
        # 6. Update job with results
        db.update_resume_job(
            job_id, 
            parsed_data=parsed_data.model_dump(), 
            status="done"
        )
        
        # 7. Create analysis result
        db.create_analysis_result(
            resume_job_id=job_id,
            jd_job_id=None,
            score_total=int(score.total),
            score_breakdown=score.model_dump(),
            gaps={"missing_skills": [], "weak_bullets": []}
        )
        
        # 8. Store initial embedding (Phase 2 optimization)
        try:
            store_resume_embedding(job_id, raw_text, {"name": parsed_data.name})
        except Exception as embed_err:
            logger.warning(f"[{job_id}] Initial embedding failed: {embed_err}")
        
        logger.info(f"[{job_id}] Task complete")
        return {
            "job_id": job_id, 
            "status": "done", 
            "score_total": int(score.total)
        }

    except Exception as e:
        logger.error(f"[{job_id}] Task failed: {str(e)}")
        db.update_resume_job(job_id, status="failed", error_message=str(e))
        # Re-raise for Celery retry mechanism if appropriate
        raise self.retry(exc=e)

@celery_app.task(bind=True, name="app.workers.tasks.analyze_resume_jd_task", max_retries=2, default_retry_delay=30)
def analyze_resume_jd_task(self, resume_job_id: str, jd_job_id: str) -> dict:
    """
    Background task to compute semantic similarity and full Phase 3 ATS analysis.
    """
    logger.info(f"[{resume_job_id}] JD analysis task started")
    try:
        # 1. Fetch data from DB
        resume_job = db.get_resume_job(resume_job_id)
        jd_job = db.get_jd_job(jd_job_id)
        
        if not resume_job or not jd_job:
            raise ValueError("Resume or JD job not found")
            
        parsed_resume = ResumeData(**resume_job["parsed_data"])
        parsed_jd = JDData(**jd_job["parsed_data"])
        raw_resume_text = resume_job["raw_text"]
        
        # 2. Get Semantic Similarity
        logger.info(f"[{resume_job_id}] Computing semantic similarity")
        similarity = compute_similarity(resume_job_id, jd_job_id)
        
        # 3. Fallback: Generate embeddings if missing in Qdrant
        if similarity == 0.0:
            logger.info(f"[{resume_job_id}] Embeddings missing or match failed, generating/verifying...")
            store_resume_embedding(resume_job_id, raw_resume_text, {"name": parsed_resume.name})
            store_jd_embedding(jd_job_id, jd_job["raw_text"], {"role_title": parsed_jd.role_title})
            similarity = compute_similarity(resume_job_id, jd_job_id)

        logger.info(f"[{resume_job_id}] Similarity: {similarity:.3f}")
        
        # 4. Compute JD-aware score
        score = compute_ats_score_with_jd(
            parsed_resume, 
            parsed_jd, 
            similarity, 
            raw_resume_text
        )
        
        # 5. Phase 3: Gap Detection
        logger.info(f"[{resume_job_id}] Running gap detection")
        gaps = detect_gaps(parsed_resume, parsed_jd)
        
        # 6. Phase 3: Formatting Check
        logger.info(f"[{resume_job_id}] Checking formatting")
        formatting = check_formatting(raw_resume_text, parsed_resume)
        
        # 7. Phase 3: Enhance Weak Bullets
        enhancements = []
        if gaps["weak_bullets"]:
            logger.info(f"[{resume_job_id}] Enhancing {len(gaps['weak_bullets'])} weak bullets")
            enhancements = enhance_weak_bullets(
                gaps["weak_bullets"],
                parsed_jd.role_title,
                parsed_jd.required_skills
            )
            
        # 8. Phase 3: Generate Learning Path
        logger.info(f"[{resume_job_id}] Generating learning path")
        learning_path = generate_learning_path(
            gaps["missing_skills"],
            gaps["preferred_missing"],
            parsed_jd.role_title
        )
        
        # 9. Phase 3: Generate Feedback
        logger.info(f"[{resume_job_id}] Generating coaching feedback")
        matched_skills = get_matched_skills(parsed_resume.skills, parsed_jd)
        feedback = generate_feedback(
            role_title=parsed_jd.role_title,
            score_total=int(score.total),
            score_label=get_score_label(score.total),
            semantic_similarity=similarity,
            matched_skills=matched_skills,
            parsed_resume=parsed_resume,
            weak_bullet_count=len(gaps["weak_bullets"]),
            formatting_issues=formatting["ats_issues"]
        )
        
        # 10. Save results to DB
        db.create_analysis_result(
            resume_job_id=resume_job_id,
            jd_job_id=jd_job_id,
            score_total=int(score.total),
            score_breakdown=score.model_dump(),
            gaps=gaps,
            enhancements=enhancements,
            compliance_issues=formatting,
            feedback_text=feedback,
            learning_path=learning_path,
            semantic_similarity=similarity,
            matched_skills=matched_skills
        )
        
        logger.info(f"[{resume_job_id}] Full Phase 3 analysis complete. Score: {score.total}")
        return {
            "resume_job_id": resume_job_id,
            "jd_job_id": jd_job_id,
            "score_total": int(score.total),
            "status": "done"
        }

    except Exception as e:
        logger.error(f"[{resume_job_id}] JD Analysis failed: {str(e)}")
        raise self.retry(exc=e)

@celery_app.task
def health_check_task():
    return "ok"

def run_pipeline_sync(job_id: str):
    """
    Synchronous fallback for testing without a Celery worker.
    """
    return process_resume_task(None, job_id)
