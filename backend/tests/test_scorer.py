from app.core.scorer import (
    score_skills_baseline, 
    score_experience_baseline, 
    compute_ats_score_baseline,
    get_score_label
)
from app.models.schemas import ResumeData

def test_score_skills_no_skills():
    assert score_skills_baseline([]) == 0.0

def test_score_skills_many_skills():
    skills = [f"Skill {i}" for i in range(25)]
    score = score_skills_baseline(skills)
    assert score >= 80.0

def test_score_experience_empty():
    assert score_experience_baseline([]) == 0.0

def test_score_experience_quality():
    exp = [
        {
            "company": "Test",
            "role": "Dev",
            "duration_months": 24,
            "bullets": ["Did 50% more work", "Used Python", "Managed 3 people"]
        }
    ]
    score = score_experience_baseline(exp)
    assert score > 40.0 # Base + duration + quality

def test_compute_ats_score_weights():
    # Weights are: 0.4, 0.25, 0.15, 0.1, 0.1
    from shared.constants import SCORE_WEIGHTS
    assert sum(SCORE_WEIGHTS.values()) == pytest.approx(1.0)

def test_score_label():
    assert get_score_label(20) == "Needs Significant Work"
    assert get_score_label(45) == "Below Average"
    assert get_score_label(60) == "Average"
    assert get_score_label(75) == "Good"
    assert get_score_label(85) == "Strong"
    assert get_score_label(95) == "Excellent"

import pytest
