import logging
from typing import List, Dict, Any
from app.db.postgres_client import db
from app.core.embeddings import compute_similarity

logger = logging.getLogger(__name__)

def rank_resumes(resume_job_ids: List[str], jd_job_id: str) -> List[Dict[str, Any]]:
    """
    Ranks multiple resumes against a single JD.
    """
    ranked_results = []
    
    for job_id in resume_job_ids:
        # 1. Fetch data
        resume_job = db.get_resume_job(job_id)
        if not resume_job:
            continue
            
        # 2. Try to find existing analysis
        analysis = db.get_analysis_result(job_id)
        
        score_total = 0
        score_breakdown = {}
        similarity = 0.0
        matched_count = 0
        missing_count = 0
        top_skills = []
        
        # Check if analysis matches THIS JD
        if analysis and str(analysis.get("jd_job_id")) == str(jd_job_id):
            score_total = analysis["score_total"]
            score_breakdown = analysis["score_breakdown"]
            similarity = analysis["semantic_similarity"] or 0.0
            matched_count = len(analysis["matched_skills"].get("required_matched", []))
            missing_count = len(analysis["matched_skills"].get("required_missing", []))
            top_skills = analysis["matched_skills"].get("required_matched", [])[:5]
        else:
            # Recompute basic similarity on the fly
            similarity = compute_similarity(job_id, jd_job_id)
            # If no analysis, we use baseline score as placeholder or just 0
            if analysis:
                 score_total = analysis["score_total"]
                 score_breakdown = analysis["score_breakdown"]
            
        # Recommendation
        recommendation = "Weak fit for this role"
        if score_total >= 80: recommendation = "Top candidate — strongly recommend interview"
        elif score_total >= 70: recommendation = "Strong candidate — recommend interview"
        elif score_total >= 60: recommendation = "Good candidate — worth considering"
        elif score_total >= 40: recommendation = "Moderate fit — consider if pipeline is thin"

        ranked_results.append({
            "resume_job_id": job_id,
            "candidate_name": resume_job["parsed_data"].get("name", "Unknown") if resume_job.get("parsed_data") else "Unknown",
            "score_total": int(score_total),
            "score_breakdown": score_breakdown,
            "semantic_similarity": round(float(similarity), 3),
            "matched_skills_count": matched_count,
            "missing_skills_count": missing_count,
            "top_matched_skills": top_skills,
            "recommendation": recommendation
        })
        
    # Sort by score
    ranked_results.sort(key=lambda x: x["score_total"], reverse=True)
    
    # Assign rank
    for i, entry in enumerate(ranked_results):
        entry["rank"] = i + 1
        
    return ranked_results

def get_ranking_summary(ranked_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generates summary statistics for a ranking session.
    """
    if not ranked_results:
        return {}
        
    total = len(ranked_results)
    avg_score = sum(r["score_total"] for r in ranked_results) / total
    
    dist = {"excellent": 0, "good": 0, "average": 0, "poor": 0}
    for r in ranked_results:
        s = r["score_total"]
        if s >= 80: dist["excellent"] += 1
        elif s >= 60: dist["good"] += 1
        elif s >= 40: dist["average"] += 1
        else: dist["poor"] += 1
        
    return {
        "total_resumes": total,
        "top_candidate": ranked_results[0]["candidate_name"],
        "average_score": round(avg_score, 1),
        "score_distribution": dist,
        "most_common_missing_skill": "N/A" # Simple implementation, could be expanded
    }
