import logging
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.config import settings
from app.models.schemas import ResumeData
from app.shared.constants import PARSER_LLM_MODEL

logger = logging.getLogger(__name__)

# Initialize LLM (GPT-4o-mini is enough for summary feedback)
llm = ChatOpenAI(
    openai_api_base=settings.OPENROUTER_BASE_URL,
    openai_api_key=settings.OPENROUTER_API_KEY,
    model_name=PARSER_LLM_MODEL,
    temperature=0.4,
    max_tokens=1000,
    default_headers={
        "HTTP-Referer": "https://github.com/ats-resume-scanner",
        "X-Title": "ATS Resume Scanner - Explainability"
    }
)

SYSTEM_PROMPT = """
You are a career coach providing honest, constructive feedback on a candidate's resume match for a specific job role.
Be direct, specific, and actionable. Avoid generic advice.
Write in the second person ("Your resume...", "You should...").
Keep the response under 200 words.

Structure your response as 3 short paragraphs:
1. Overall assessment of the match.
2. Top 2-3 strengths found in the resume.
3. Top 2-3 specific improvements needed to better align with the job description.
"""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", """
Role: {role_title}
ATS Score: {score_total}/100 ({score_label})
Semantic Similarity: {similarity_percentage}%

Matched required skills: {required_matched}
Missing required skills: {required_missing}

Experience: {experience_summary}
Projects: {project_summary}

Weak bullets found: {weak_bullet_count}
Formatting issues: {formatting_issues}

Write honest, specific career coaching feedback:
""")
])

# Chain
explainability_chain = prompt_template | llm | StrOutputParser()

def generate_feedback(
    role_title: str,
    score_total: int,
    score_label: str,
    semantic_similarity: float,
    matched_skills: Dict[str, List[str]],
    parsed_resume: ResumeData,
    weak_bullet_count: int,
    formatting_issues: List[Dict[str, Any]]
) -> str:
    """
    Generates human-readable feedback using LLM.
    """
    try:
        experience_summary = f"{len(parsed_resume.experience)} roles, {sum(e.duration_months for e in parsed_resume.experience)} months total"
        project_summary = f"{len(parsed_resume.projects)} projects: {', '.join(p.name for p in parsed_resume.projects[:2])}"
        similarity_percentage = round(semantic_similarity * 100, 1)
        
        format_issues_text = ", ".join([i["issue"] for i in formatting_issues]) if formatting_issues else "None"
        
        response = explainability_chain.invoke({
            "role_title": role_title,
            "score_total": score_total,
            "score_label": score_label,
            "similarity_percentage": similarity_percentage,
            "required_matched": ", ".join(matched_skills.get("required_matched", [])),
            "required_missing": ", ".join(matched_skills.get("required_missing", [])),
            "experience_summary": experience_summary,
            "project_summary": project_summary,
            "weak_bullet_count": weak_bullet_count,
            "formatting_issues": format_issues_text
        })
        
        return response.strip()
    except Exception as e:
        logger.error(f"Failed to generate feedback: {e}")
        return "Your resume has been analyzed. Please review the score and skill gaps below for specific improvements."
