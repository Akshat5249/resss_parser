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

# System Prompt
SYSTEM_PROMPT = """
You are an expert Job Description analyzer. Your task is to extract structured requirements from the provided job description text.
Extract the following fields:
- role_title: The exact job title.
- required_skills: A list of mandatory technical and soft skills.
- preferred_skills: A list of nice-to-have or optional skills.
- min_experience_years: The minimum years of experience required (extract as an integer, default to 0).
- responsibilities: A list of key duties and tasks.
- nice_to_have: A list of other preferred qualifications or perks.

Strict rules:
1. Return ONLY valid JSON that matches the provided schema.
2. Do not include any explanation or conversational text.
3. If a field is not found, use an empty list or 0 as appropriate.
4. Be precise with required vs preferred skills.
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
