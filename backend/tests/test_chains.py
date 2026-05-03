import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.chains.resume_parser_chain import parse_resume, resume_parser_chain

def test_chain_structure():
    assert resume_parser_chain is not None

@patch("app.chains.resume_parser_chain.resume_parser_chain.invoke")
def test_parse_resume_success(mock_invoke):
    mock_invoke.return_value = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "1234567890",
        "skills": ["Python", "FastAPI"],
        "experience": [],
        "education": [],
        "projects": [],
        "summary": "Experienced dev"
    }
    result = parse_resume("Raw text")
    assert result.name == "John Doe"
    assert "Python" in result.skills

@patch("app.chains.resume_parser_chain.resume_parser_chain.invoke")
def test_parse_resume_failure(mock_invoke):
    mock_invoke.side_effect = Exception("LLM Error")
    with pytest.raises(HTTPException) as exc:
        parse_resume("Raw text")
    assert exc.value.status_code == 500
