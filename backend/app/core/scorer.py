import re
import logging
from typing import List, Dict, Any
from app.models.schemas import ResumeData, ScoreBreakdown
from app.shared.constants import SCORE_WEIGHTS

logger = logging.getLogger(__name__)

IN_DEMAND_SKILLS = [
    "Python", "JavaScript", "TypeScript", "React", "Node.js", "AWS", "Docker", "Kubernetes",
    "Machine Learning", "SQL", "PostgreSQL", "FastAPI", "Git", "CI/CD", "REST API",
    "LangChain", "PyTorch", "TensorFlow", "MongoDB", "Redis"
]

def score_skills_baseline(skills: List[str]) -> float:
    """
    Scores 0–100 based on quantity and quality of skills.
    """
    if not skills:
        return 0.0
    
    # Quantity score (up to 70 points)
    count = len(skills)
    quantity_score = min(count * 5, 70)
    
    # In-demand bonus (up to 30 points)
    in_demand_count = sum(1 for s in skills if s in IN_DEMAND_SKILLS)
    bonus_score = min(in_demand_count * 3, 30)
    
    return float(min(quantity_score + bonus_score, 100))

def score_experience_baseline(experience: List[Any]) -> float:
    """
    Scores 0–100 based on number of jobs, duration, and depth (metrics/bullets).
    Refined to avoid penalizing high-quality internships/student resumes.
    """
    if not experience:
        return 0.0
    
    # 1. Base Score for having experience (up to 30 points)
    job_count = len(experience)
    job_count_score = min(job_count * 20, 30) # 1 job = 20, 2+ jobs = 30
    
    # 2. Total duration (up to 30 points)
    total_months = sum(exp.get('duration_months', 0) if isinstance(exp, dict) else exp.duration_months for exp in experience)
    # 3 points per 6 months, max 5 years (60 months)
    duration_score = min((total_months / 6) * 3, 30) 
    
    # 3. Quality & Metrics (up to 40 points + bonus)
    quality_score = 0
    metric_pattern = re.compile(r'\d+[%x$k\+]|reduction|improvement|optimization|latency|faster|scale')
    
    total_bullets = 0
    total_metrics = 0
    
    for exp in experience:
        bullets = exp.get('bullets', []) if isinstance(exp, dict) else exp.bullets
        total_bullets += len(bullets)
        
        # High bullet count per job (depth)
        if len(bullets) >= 4:
            quality_score += 10
        elif len(bullets) >= 2:
            quality_score += 5
            
        # Metric density
        job_metrics = sum(1 for b in bullets if metric_pattern.search(b.lower()))
        total_metrics += job_metrics
        quality_score += min(job_metrics * 10, 25) # Up to 25 points for metrics in a single job

    # Cap quality score but allow bonus for high impact
    final_quality = min(quality_score, 40)
    
    # High-impact bonus: If metrics-to-job ratio is high
    impact_bonus = 0
    if job_count > 0 and (total_metrics / job_count) >= 2:
        impact_bonus = 10

    return float(min(job_count_score + duration_score + final_quality + impact_bonus, 100))

def score_projects_baseline(projects: List[Any]) -> float:
    """
    Scores 0–100 based on quantity and quality of projects.
    """
    if not projects:
        return 0.0
    
    # Quantity (up to 50 points)
    project_count = len(projects)
    quantity_score = min(project_count * 25, 50)
    
    # Quality (up to 50 points)
    quality_score = 0
    for proj in projects:
        tech_stack = proj.get('tech_stack', []) if isinstance(proj, dict) else proj.tech_stack
        impact = proj.get('impact', "") if isinstance(proj, dict) else proj.impact
        
        if len(tech_stack) >= 2:
            quality_score += 15
        if len(impact) > 30:
            quality_score += 15
            
    return float(min(quantity_score + quality_score, 100))

def score_education_baseline(education: List[Any]) -> float:
    """
    Scores 0–100 based on degree level and relevance.
    """
    if not education:
        return 0.0
    
    score = 30.0 # Base points
    
    degree_levels = {
        "bachelor": 40,
        "bs": 40,
        "master": 55,
        "ms": 55,
        "phd": 70,
        "doctorate": 70
    }
    
    relevant_fields = ["cs", "computer science", "engineering", "data science", "it", "mathematics", "software"]
    
    max_degree_bonus = 0
    field_bonus = 0
    
    for edu in education:
        degree = (edu.get('degree', "") if isinstance(edu, dict) else edu.degree).lower()
        field = (edu.get('field', "") if isinstance(edu, dict) else edu.field).lower()
        
        for level, bonus in degree_levels.items():
            if level in degree:
                max_degree_bonus = max(max_degree_bonus, bonus)
        
        if any(rf in field for rf in relevant_fields):
            field_bonus = 20
            
    return float(min(score + max_degree_bonus + field_bonus, 100))

def score_formatting_baseline(raw_text: str, parsed_data: ResumeData) -> float:
    """
    Scores 0–100 based on structural signals.
    """
    score = 0.0
    
    # Section Presence (60 points)
    if parsed_data.experience: score += 20
    if parsed_data.education: score += 20
    if parsed_data.skills: score += 20
    
    # Contact Info (20 points)
    if parsed_data.email: score += 10
    if parsed_data.phone: score += 10
    
    # Word count sanity (20 points)
    word_count = len(raw_text.split())
    if 300 <= word_count <= 1200:
        score += 20
    elif word_count > 1200:
        score += 10
        
    return float(max(0, min(score, 100)))

def compute_ats_score_baseline(parsed_data: ResumeData, raw_text: str) -> ScoreBreakdown:
    """
    Computes the weighted baseline ATS score.
    """
    scores = {
        "skill_match": score_skills_baseline(parsed_data.skills),
        "experience": score_experience_baseline(parsed_data.experience),
        "projects": score_projects_baseline(parsed_data.projects),
        "education": score_education_baseline(parsed_data.education),
        "formatting": score_formatting_baseline(raw_text, parsed_data)
    }
    
    total = sum(scores[k] * SCORE_WEIGHTS[k] for k in scores)
    
    return ScoreBreakdown(
        skill_match=scores["skill_match"],
        experience=scores["experience"],
        projects=scores["projects"],
        education=scores["education"],
        formatting=scores["formatting"],
        total=round(total)
    )

def get_matched_skills(resume_skills: List[str], jd: Any) -> Dict[str, List[str]]:
    """
    Identifies matched and missing skills between a resume and a JD.
    """
    resume_skills_set = {s.lower() for s in resume_skills}
    
    required_matched = [s for s in jd.required_skills if s.lower() in resume_skills_set]
    required_missing = [s for s in jd.required_skills if s.lower() not in resume_skills_set]
    
    preferred_matched = [s for s in jd.preferred_skills if s.lower() in resume_skills_set]
    preferred_missing = [s for s in jd.preferred_skills if s.lower() not in resume_skills_set]
    
    return {
        "required_matched": required_matched,
        "required_missing": required_missing,
        "preferred_matched": preferred_matched,
        "preferred_missing": preferred_missing
    }

def compute_ats_score_with_jd(
    parsed_resume: ResumeData,
    parsed_jd: Any,
    semantic_similarity: float,
    raw_resume_text: str
) -> ScoreBreakdown:
    """
    Computes a JD-aware ATS score.
    """
    # 1. Skill Match (40%)
    matched = get_matched_skills(parsed_resume.skills, parsed_jd)
    
    required_count = max(len(parsed_jd.required_skills), 1)
    preferred_count = max(len(parsed_jd.preferred_skills), 1)
    
    required_score = (len(matched["required_matched"]) / required_count) * 100
    preferred_score = (len(matched["preferred_matched"]) / preferred_count) * 100
    
    # Semantic boost (up to 20 points added to skill score)
    semantic_boost = semantic_similarity * 20
    skill_score = min(100, (required_score * 0.7) + (preferred_score * 0.2) + semantic_boost)
    
    # 2. Experience (25%)
    total_months = sum(exp.duration_months for exp in parsed_resume.experience)
    required_months = parsed_jd.min_experience_years * 12
    
    if required_months == 0:
        exp_score = 80.0 # Base if no experience required
    else:
        exp_score = min(100, (total_months / required_months) * 100)
    
    # Quality bonus (metrics detection)
    metric_pattern = re.compile(r'\d+[%x$k\+]|reduction|improvement|optimization|latency|faster|scale')
    metric_count = sum(1 for exp in parsed_resume.experience for b in exp.bullets if metric_pattern.search(b.lower()))
    exp_score = min(100, exp_score + (metric_count * 5))
    
    # 3. Projects (15%)
    # Overlap between project tech stacks and JD skills
    jd_all_skills = {s.lower() for s in parsed_jd.required_skills + parsed_jd.preferred_skills}
    project_tech_overlap = sum(
        1 for proj in parsed_resume.projects for tech in proj.tech_stack if tech.lower() in jd_all_skills
    )
    project_score = min(100, (project_tech_overlap * 10) + (len(parsed_resume.projects) * 15))
    
    # 4. Education (10%)
    edu_score = score_education_baseline(parsed_resume.education)
    
    # 5. Formatting (10%)
    format_score = score_formatting_baseline(raw_resume_text, parsed_resume)
    
    # Calculate Weighted Total
    scores = {
        "skill_match": skill_score,
        "experience": exp_score,
        "projects": project_score,
        "education": edu_score,
        "formatting": format_score
    }
    
    total = sum(scores[k] * SCORE_WEIGHTS[k] for k in scores)
    
    return ScoreBreakdown(
        skill_match=skill_score,
        experience=exp_score,
        projects=project_score,
        education=edu_score,
        formatting=format_score,
        total=round(total)
    )

def get_score_label(total: float) -> str:
    """
    Returns a human-readable interpretation of the ATS score.
    """
    if total <= 30: return "Needs Significant Work"
    if total <= 50: return "Below Average"
    if total <= 65: return "Average"
    if total <= 80: return "Good"
    if total <= 90: return "Strong"
    return "Excellent"
