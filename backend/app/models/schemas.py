from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID

# --- Core Data Models ---

class ExperienceItem(BaseModel):
    company: Optional[str] = ""
    role: Optional[str] = ""
    duration_months: Optional[int] = 0
    bullets: List[str] = []

class EducationItem(BaseModel):
    institution: Optional[str] = ""
    degree: Optional[str] = ""
    field: Optional[str] = ""
    graduation_year: Optional[int] = None

class ProjectItem(BaseModel):
    name: Optional[str] = ""
    description: Optional[str] = ""
    tech_stack: List[str] = []
    impact: Optional[str] = ""

class ResumeData(BaseModel):
    name: Optional[str] = "Unknown"
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    skills: List[str] = []
    experience: List[ExperienceItem] = []
    education: List[EducationItem] = []
    projects: List[ProjectItem] = []
    summary: Optional[str] = ""

class JDData(BaseModel):
    role_title: str
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    min_experience_years: Optional[int] = 0
    responsibilities: List[str] = []
    nice_to_have: List[str] = []

class ScoreBreakdown(BaseModel):
    skill_match: float = Field(default=0.0, ge=0, le=100)
    experience: float = Field(default=0.0, ge=0, le=100)
    projects: float = Field(default=0.0, ge=0, le=100)
    education: float = Field(default=0.0, ge=0, le=100)
    formatting: float = Field(default=0.0, ge=0, le=100)
    total: float = Field(default=0.0, ge=0, le=100)

class GapAnalysis(BaseModel):
    missing_skills: List[str] = []
    weak_bullets: List[str] = []
    over_qualified: bool = False
    under_qualified: bool = False

# --- Request/Response Models ---

class UploadResumeResponse(BaseModel):
    job_id: UUID
    task_id: Optional[str] = None
    filename: str
    status: str
    message: Optional[str] = None
    char_count: int
    parsed_data: Optional[ResumeData] = None
    score: Optional[ScoreBreakdown] = None
    score_label: Optional[str] = None

class AnalyzeRequest(BaseModel):
    resume_job_id: UUID
    jd_job_id: Optional[UUID] = None

class AnalyzeResponse(BaseModel):
    task_id: str
    status: str
    message: str

class ScoreResponse(BaseModel):
    job_id: UUID
    score: ScoreBreakdown
    created_at: datetime

class AnalysisResultResponse(BaseModel):
    job_id: UUID
    score: ScoreBreakdown
    gaps: GapAnalysis
    enhancements: List[str] = []
    compliance_issues: List[str] = []
    feedback: Optional[str] = ""
    learning_path: List[Dict[str, str]] = []

class RankRequest(BaseModel):
    jd_job_id: str
    resume_job_ids: List[str]

class RankingEntry(BaseModel):
    rank: int
    resume_job_id: str
    candidate_name: str
    score_total: int
    semantic_similarity: float
    matched_skills_count: int
    missing_skills_count: int
    top_matched_skills: List[str]
    recommendation: str

class RankingResponse(BaseModel):
    session_id: str
    jd_job_id: str
    summary: Dict
    rankings: List[RankingEntry]
    created_at: datetime

class ReportRequest(BaseModel):
    resume_job_id: str
    jd_job_id: Optional[str] = None
