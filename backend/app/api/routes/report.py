import logging
import io
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from uuid import UUID

from app.db.postgres_client import db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/report", tags=["Report"])

def _get_score_label(score: int) -> str:
    """Helper to get human readable score label for PDF."""
    if score >= 90: return "Excellent"
    if score >= 80: return "Strong"
    if score >= 66: return "Good"
    if score >= 51: return "Average"
    if score >= 31: return "Below Average"
    return "Needs Work"

@router.get("/{resume_job_id}")
async def get_report(resume_job_id: str):
    """
    Generates and returns the ATS report PDF with safe null handling.
    """
    # 1. Fetch resume job
    resume_job = db.get_resume_job(resume_job_id)
    if not resume_job:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # 2. Fetch most recent analysis result
    analysis = db.get_analysis_result(resume_job_id)
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No analysis found. Run an analysis first."
        )
    
    # Helper to safely parse jsonb fields
    def safe_json(field, default):
        if field is None:
            return default
        if isinstance(field, (dict, list)):
            return field
        try:
            return json.loads(field)
        except Exception:
            return default
    
    # PDF FIX 3: Better role_title extraction
    jd_job_id = analysis.get("jd_job_id")
    role_title = ""
    
    if jd_job_id:
        try:
            jd_job = db.get_jd_job(jd_job_id)
            if jd_job:
                jd_parsed = safe_json(jd_job.get("parsed_data"), {})
                role_title = jd_parsed.get("role_title", "")
        except Exception as e:
            logger.warning(f"Could not fetch JD for role title: {e}")
    
    # Also try from matched_skills payload
    if not role_title:
        matched = safe_json(analysis.get("matched_skills"), {})
        role_title = matched.get("role_title", "")
    
    # 3. Build analysis_data with safe defaults for every field
    score_breakdown = safe_json(analysis.get("score_breakdown"), {})
    
    analysis_data = {
        "candidate_name": (
            safe_json(resume_job.get("parsed_data"), {})
            .get("name", "Candidate")
        ),
        "role_title": role_title or "",
        "score_total": analysis.get("score_total") or 0,
        "score": {
            "skill_match": score_breakdown.get("skill_match", 0),
            "experience": score_breakdown.get("experience", 0),
            "projects": score_breakdown.get("projects", 0),
            "education": score_breakdown.get("education", 0),
            "formatting": score_breakdown.get("formatting", 0),
            "total": score_breakdown.get("total", 0),
        },
        "matched_skills": safe_json(analysis.get("matched_skills"), {
            "required_matched": [],
            "required_missing": [],
            "preferred_matched": [],
            "preferred_missing": []
        }),
        "gaps": safe_json(analysis.get("gaps"), {
            "missing_skills": [],
            "preferred_missing": [],
            "weak_bullets": [],
            "experience_gap": {
                "has_gap": False,
                "resume_months": 0,
                "required_months": 0,
                "gap_months": 0
            },
            "overall_gap_severity": "low"
        }),
        "enhancements": safe_json(analysis.get("enhancements"), []),
        "formatting": safe_json(analysis.get("compliance_issues"), {
            "compliance_score": 100,
            "is_ats_friendly": True,
            "ats_issues": [],
            "contact_info": {},
            "sections_present": {}
        }),
        "learning_path": safe_json(analysis.get("learning_path"), {
            "priority_skills": [],
            "total_estimated_weeks": 0,
            "recommended_order": [],
            "summary": ""
        }),
        "feedback": analysis.get("feedback_text") or "No feedback generated.",
        "semantic_similarity": analysis.get("semantic_similarity") or 0,
        "created_at": str(analysis.get("created_at", "")),
    }
    
    analysis_data["score_label"] = _get_score_label(
        analysis_data["score_total"]
    )
    
    # 4. Generate PDF
    try:
        from app.core.pdf_generator import generate_ats_report
        pdf_bytes = generate_ats_report(analysis_data)
        
        candidate_name = analysis_data["candidate_name"].replace(" ", "_")
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="ATS_Report_{candidate_name}.pdf"'
            }
        )
    except Exception as e:
        logger.error(f"PDF generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF: {str(e)}"
        )

@router.post("/{resume_job_id}/store")
async def store_report(resume_job_id: str):
    """
    Placeholder for Phase 4 storage requirement.
    """
    return {"message": "Use GET /report/{id} to download the PDF report."}
