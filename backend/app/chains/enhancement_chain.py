import logging
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.config import settings
from app.shared.constants import ENHANCEMENT_LLM_MODEL

logger = logging.getLogger(__name__)

# Initialize High-Quality LLM (GPT-4o)
llm = ChatOpenAI(
    openai_api_base=settings.OPENROUTER_BASE_URL,
    openai_api_key=settings.OPENROUTER_API_KEY,
    model_name=ENHANCEMENT_LLM_MODEL,
    temperature=0.3,
    max_tokens=2000,
    default_headers={
        "HTTP-Referer": "https://github.com/ats-resume-scanner",
        "X-Title": "ATS Resume Scanner - Enhancement"
    }
)

# Prompts
SYSTEM_PROMPT = """
You are an expert resume writer and career coach. 
Your job is to rewrite weak resume bullet points to be stronger, more impactful, and ATS-friendly.

Rules for rewriting:
1. Start with a strong action verb (e.g., Built, Developed, Engineered, Optimized).
2. Add specific metrics where implied or reasonable. If the original implies an improvement, use placeholders like "X%" if you can't infer it.
3. Include relevant technology/tools mentioned in the context.
4. Focus on impact and outcomes, not just tasks.
5. Keep the rewrite concise (under 2 lines).
6. Do NOT fabricate specific numbers that aren't implied by the original text.
7. Return ONLY the rewritten bullet, no explanation or conversational text.
"""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Original bullet: {bullet}\nJob context: {job_context}\nIssues identified: {issues}\n\nRewrite this bullet to be stronger:")
])

# Chain
enhancement_chain = prompt_template | llm | StrOutputParser()

def enhance_bullet(bullet: str, job_context: str, issues: List[str]) -> str:
    """
    Invokes the LLM to rewrite a single weak bullet point.
    """
    try:
        response = enhancement_chain.invoke({
            "bullet": bullet,
            "job_context": job_context,
            "issues": ", ".join(issues)
        })
        return response.strip()
    except Exception as e:
        logger.error(f"Failed to enhance bullet: {e}")
        return bullet # Fallback to original

def enhance_weak_bullets(
    weak_bullets: List[Dict[str, Any]], 
    jd_role: str, 
    jd_required_skills: List[str]
) -> List[Dict[str, Any]]:
    """
    Processes a list of weak bullets sequentially and returns their enhanced versions.
    """
    enhanced_results = []
    job_context = f"{jd_role} role requiring {', '.join(jd_required_skills[:5])}"
    
    for item in weak_bullets:
        original = item["bullet"]
        company = item["company"]
        role = item["role"]
        issues = item["issues"]
        
        logger.info(f"Enhancing bullet for {company} - {role}")
        enhanced = enhance_bullet(original, job_context, issues)
        
        enhanced_results.append({
            "original": original,
            "enhanced": enhanced,
            "company": company,
            "role": role,
            "issues": issues
        })
        
    return enhanced_results
