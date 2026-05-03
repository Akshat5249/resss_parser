import re
from typing import List, Dict, Any
from app.models.schemas import ResumeData

def check_contact_info(raw_text: str) -> Dict[str, bool]:
    """
    Checks for the presence of standard contact information.
    """
    return {
        "email": bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_text)),
        "phone": bool(re.search(r'(\+\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}', raw_text)),
        "linkedin": "linkedin.com" in raw_text.lower(),
        "github": "github.com" in raw_text.lower()
    }

def check_section_headers(raw_text: str) -> Dict[str, bool]:
    """
    Checks for standard ATS section keywords.
    """
    raw_lower = raw_text.lower()
    sections = {
        "experience": ["experience", "work experience", "employment"],
        "education": ["education", "academic"],
        "skills": ["skills", "technical skills", "core competencies"],
        "projects": ["projects", "personal projects", "academic projects"],
        "summary": ["summary", "objective", "profile", "about"]
    }
    
    return {
        name: any(keyword in raw_lower for keyword in keywords)
        for name, keywords in sections.items()
    }

def check_ats_issues(raw_text: str, parsed_data: ResumeData) -> List[Dict[str, Any]]:
    """
    Checks for common ATS compatibility issues.
    """
    issues = []
    
    # 1. Table layout detection (heuristic: lots of whitespace in chunks)
    if re.search(r' {4,}', raw_text) and len(re.findall(r'\n', raw_text)) < len(raw_text) / 50:
        issues.append({
            "issue": "possible table layout", 
            "severity": "high",
            "suggestion": "Use single-column layout for ATS compatibility"
        })
        
    # 2. Special characters
    special_chars = ["□", "■", "●", "★", "☆", "✓", "✗", "→", "←", "↑", "↓"]
    found_chars = [c for c in special_chars if c in raw_text]
    if found_chars:
        issues.append({
            "issue": "special characters detected", 
            "severity": "medium",
            "suggestion": "Replace decorative characters with plain text bullets or ASCII characters"
        })
        
    # 3. Word count
    word_count = len(raw_text.split())
    if word_count < 300:
        issues.append({
            "issue": "resume too short", 
            "severity": "high",
            "suggestion": "Add more detail to experience and projects sections"
        })
    elif word_count > 700 and len(parsed_data.experience) <= 2:
        issues.append({
            "issue": "resume may be too long", 
            "severity": "low",
            "suggestion": "Consider condensing content to keep it under 1 page for your experience level"
        })
        
    # 4. Section headers
    headers = check_section_headers(raw_text)
    if not headers["experience"]:
        issues.append({
            "issue": "missing section: experience", 
            "severity": "high",
            "suggestion": "Add a clear Experience section with a standard header"
        })
    if not headers["skills"]:
        issues.append({
            "issue": "missing section: skills", 
            "severity": "high",
            "suggestion": "Add a dedicated Skills section"
        })
        
    # 5. Keyword stuffing
    all_skills_flat = " ".join(parsed_data.skills).lower()
    for skill in set(parsed_data.skills):
        if len(skill) > 3 and raw_text.lower().count(skill.lower()) > 5:
            issues.append({
                "issue": f"keyword stuffing: {skill}", 
                "severity": "low",
                "suggestion": f"Avoid repeating '{skill}' excessively; list it once in skills."
            })
            
    return issues

def check_formatting(raw_text: str, parsed_data: ResumeData) -> Dict[str, Any]:
    """
    Main formatting check master function.
    """
    contact_info = check_contact_info(raw_text)
    sections = check_section_headers(raw_text)
    ats_issues = check_ats_issues(raw_text, parsed_data)
    
    # compliance_score calculation
    score = 100
    for issue in ats_issues:
        if issue["severity"] == "high": score -= 20
        elif issue["severity"] == "medium": score -= 10
        elif issue["severity"] == "low": score -= 5
        
    if not contact_info["email"]: score -= 15
    if not sections["experience"]: score -= 20
    
    return {
        "contact_info": contact_info,
        "sections_present": sections,
        "ats_issues": ats_issues,
        "compliance_score": float(max(0, score)),
        "is_ats_friendly": score >= 70
    }
