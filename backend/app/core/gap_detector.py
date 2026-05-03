import re
from typing import List, Dict, Any
from app.models.schemas import ResumeData, JDData

STRONG_ACTION_VERBS = [
    "Built", "Developed", "Designed", "Implemented", "Led", "Created", "Optimized",
    "Reduced", "Increased", "Improved", "Deployed", "Architected", "Engineered",
    "Launched", "Delivered", "Automated", "Integrated", "Migrated", "Scaled",
    "Achieved", "Generated", "Saved", "Managed", "Mentored", "Established",
    "Streamlined", "Accelerated", "Transformed", "Pioneered", "Drove"
]

def detect_missing_skills(resume_skills: List[str], jd: JDData) -> Dict[str, Any]:
    """
    Compares resume skills against JD requirements (case-insensitive).
    """
    resume_skills_set = {s.lower() for s in resume_skills}
    
    required_matched = [s for s in jd.required_skills if s.lower() in resume_skills_set]
    required_missing = [s for s in jd.required_skills if s.lower() not in resume_skills_set]
    
    preferred_matched = [s for s in jd.preferred_skills if s.lower() in resume_skills_set]
    preferred_missing = [s for s in jd.preferred_skills if s.lower() not in resume_skills_set]
    
    match_percentage = (len(required_matched) / max(len(jd.required_skills), 1)) * 100
    
    return {
        "required_missing": required_missing,
        "preferred_missing": preferred_missing,
        "required_matched": required_matched,
        "preferred_matched": preferred_matched,
        "match_percentage": round(match_percentage, 2)
    }

def detect_weak_bullets(experience: List[Any]) -> List[Dict[str, Any]]:
    """
    Analyzes experience bullets to identify points that need improvement.
    """
    weak_bullets = []
    metric_pattern = re.compile(r'\d+[%x$k\+]|reduction|improvement|optimization|latency|faster|scale')
    passive_voice = ["was responsible for", "helped with", "assisted in", "worked on", "involved in"]
    vague_openers = ["various", "multiple", "several", "many things"]
    
    for exp in experience:
        # Handle both dict and Pydantic model
        company = exp.company if hasattr(exp, 'company') else exp.get('company', 'Unknown')
        role = exp.role if hasattr(exp, 'role') else exp.get('role', 'Unknown')
        bullets = exp.bullets if hasattr(exp, 'bullets') else exp.get('bullets', [])
        
        for bullet in bullets:
            issues = []
            
            # 1. Too short
            if len(bullet.split()) < 8:
                issues.append("too short")
            
            # 2. Passive voice / Vague openers
            bullet_lower = bullet.lower()
            if any(p in bullet_lower for p in passive_voice):
                issues.append("passive voice")
            if any(bullet_lower.startswith(v) for v in vague_openers):
                issues.append("vague opener")
                
            # 3. No action verb at start
            first_word = bullet.strip().split()[0].rstrip(',.') if bullet.strip() else ""
            if first_word.title() not in STRONG_ACTION_VERBS:
                issues.append("weak or missing action verb")
                
            # 4. No metrics
            if not metric_pattern.search(bullet_lower):
                issues.append("no quantifiable metrics")
                
            if issues:
                severity = "high" if len(issues) >= 3 else "medium" if len(issues) >= 2 else "low"
                weak_bullets.append({
                    "company": company,
                    "role": role,
                    "bullet": bullet,
                    "issues": issues,
                    "severity": severity
                })
                
    return weak_bullets

def detect_gaps(parsed_resume: ResumeData, parsed_jd: JDData) -> Dict[str, Any]:
    """
    Main function for comprehensive gap analysis.
    """
    skills_analysis = detect_missing_skills(parsed_resume.skills, parsed_jd)
    weak_bullets = detect_weak_bullets(parsed_resume.experience)
    
    # Experience gap check
    resume_total_months = sum(exp.duration_months for exp in parsed_resume.experience)
    required_months = parsed_jd.min_experience_years * 12
    gap_months = max(0, required_months - resume_total_months)
    
    # Project relevance
    jd_req_skills_set = {s.lower() for s in parsed_jd.required_skills}
    relevant_projects = 0
    for proj in parsed_resume.projects:
        if any(tech.lower() in jd_req_skills_set for tech in proj.tech_stack):
            relevant_projects += 1
    project_relevance = (relevant_projects / max(len(parsed_resume.projects), 1)) * 100
    
    # Overall Severity
    missing_pct = len(skills_analysis["required_missing"]) / max(len(parsed_jd.required_skills), 1)
    if missing_pct >= 0.5 or gap_months > 12:
        severity = "high"
    elif missing_pct >= 0.25 or gap_months >= 6:
        severity = "medium"
    else:
        severity = "low"
        
    return {
        "missing_skills": skills_analysis["required_missing"],
        "preferred_missing": skills_analysis["preferred_missing"],
        "weak_bullets": weak_bullets,
        "experience_gap": {
            "has_gap": gap_months > 0,
            "resume_months": resume_total_months,
            "required_months": required_months,
            "gap_months": gap_months
        },
        "project_relevance_score": round(project_relevance, 2),
        "overall_gap_severity": severity
    }
