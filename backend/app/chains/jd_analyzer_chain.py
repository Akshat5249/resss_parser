import logging
from typing import Optional
from fastapi import HTTPException
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.config import settings
from app.models.schemas import JDData
from app.shared.constants import PARSER_LLM_MODEL

logger = logging.getLogger(__name__)

# Initialize the LLM with OpenRouter config
llm = ChatOpenAI(
    openai_api_base=settings.OPENROUTER_BASE_URL,
    openai_api_key=settings.OPENROUTER_API_KEY,
    model_name=PARSER_LLM_MODEL,
    temperature=0,
    max_tokens=2000,
    default_headers={
        "HTTP-Referer": "https://github.com/ats-resume-scanner",
        "X-Title": "ATS Resume Scanner - JD Analyzer"
    }
)

# Initialize the parser
parser = JsonOutputParser(pydantic_object=JDData)

# System Prompt - FIXED BRACES FOR LANGCHAIN
SYSTEM_PROMPT = """
You are a professional job description parser. Your task is to extract structured requirements from the provided job description text.

CRITICAL RULES FOR SKILLS:
- required_skills must be SHORT skill names only (1-4 words max)
- NEVER include full sentences as skills
- NEVER include "Understanding of X" — just use "X"
- NEVER include "Experience in X" — just use "X"
- Extract the CORE TECHNOLOGY or SKILL NAME only

EXAMPLES:
BAD: "Understanding of statistical modeling and hypothesis testing"
GOOD: ["Statistical Modeling", "Hypothesis Testing"]

BAD: "Experience in creation of ML models to solve business problems"  
GOOD: ["Machine Learning", "ML Models"]

BAD: "Proficiency in Python including Pandas, Plotly, Scikit-Learn"
GOOD: ["Python", "Pandas", "Plotly", "Scikit-Learn"]

BAD: "Understanding of SQL databases and NoSQL databases"
GOOD: ["SQL", "NoSQL", "PostgreSQL"]

Extract clean, short skill/technology names only.
Each skill should be something you would write on a resume.

Return ONLY valid JSON matching this exact structure:
{{
  "role_title": "exact job title from posting",
  "required_skills": ["Skill1", "Skill2", "Skill3"],
  "preferred_skills": ["Skill4", "Skill5"],
  "min_experience_years": 0,
  "responsibilities": ["responsibility 1", "responsibility 2"],
  "nice_to_have": ["nice to have 1"]
}}

If a field is not found use empty list or 0.
Return ONLY the JSON object, no other text.
"""

# Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT + "\n\n{format_instructions}"),
    ("human", "Job Description Text:\n{jd_text}")
]).partial(format_instructions=parser.get_format_instructions())

# The Chain
jd_analyzer_chain = prompt | llm | parser

def analyze_jd(jd_text: str) -> JDData:
    """
    Invokes the LangChain chain to parse raw JD text into a structured JDData object.
    """
    try:
        response = jd_analyzer_chain.invoke({"jd_text": jd_text})
        return JDData(**response)
    except Exception as e:
        logger.error(f"JD analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"JD analysis failed: {str(e)}")
