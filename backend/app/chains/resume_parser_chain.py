import logging
from typing import Optional
from fastapi import HTTPException
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.config import settings
from app.models.schemas import ResumeData
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
        "HTTP-Referer": "https://github.com/ats-resume-scanner", # Optional but good practice for OpenRouter
        "X-Title": "ATS Resume Scanner"
    }
)

# Initialize the parser
parser = JsonOutputParser(pydantic_object=ResumeData)

# System Prompt
SYSTEM_PROMPT = """
You are a professional resume parser. Your task is to extract structured information from the provided raw resume text.
Extract the following fields:
- name, email, phone (contact information)
- summary (a 2-3 sentence professional summary)
- ALL skills mentioned anywhere in the resume (technical and soft skills)
- experience: list of entries with company, role, duration_months (estimate if not explicit), and bullet points
- education: list of entries with institution, degree, field, and graduation_year
- projects: list of entries with name, description, tech_stack (list), and impact/metrics

Strict rules:
1. Return ONLY valid JSON that matches the provided schema.
2. Do not include any explanation or conversational text.
3. If a field is not found, use an empty string for strings, 0 or null for integers, or an empty list for lists.
4. If duration is like "Jan 2020 - Dec 2020", duration_months is 12. If "2020 - Present", estimate up to current date (May 2026).
5. Extract ALL skills, don't summarize them into categories; just list them.
"""

# Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT + "\n\n{format_instructions}"),
    ("human", "Resume Text:\n{resume_text}")
]).partial(format_instructions=parser.get_format_instructions())

# The Chain
resume_parser_chain = prompt | llm | parser

def parse_resume(raw_text: str) -> ResumeData:
    """
    Invokes the LangChain chain to parse raw resume text into a structured ResumeData object.
    """
    try:
        response = resume_parser_chain.invoke({"resume_text": raw_text})
        # Ensure it's a valid ResumeData object (JsonOutputParser returns a dict)
        return ResumeData(**response)
    except Exception as e:
        logger.error(f"Resume parsing failed. Error: {str(e)}")
        if 'response' in locals():
            logger.error(f"LLM Raw Response: {response}")
        raise HTTPException(status_code=500, detail=f"Resume parsing failed during structured extraction: {str(e)}")
