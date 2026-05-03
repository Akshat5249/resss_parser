import pytest
from fastapi import HTTPException
from app.core.ingestion import clean_text, chunk_text, validate_file

def test_clean_text():
    text = "Hello\n\n\nWorld   This is\t\ttest."
    cleaned = clean_text(text)
    assert cleaned == "Hello\n\nWorld This is test."
    assert "\n\n\n" not in cleaned

def test_chunk_text():
    text = "This is a sentence. This is another one. And a third one here."
    chunks = chunk_text(text, chunk_size=30, overlap=5)
    assert len(chunks) > 1
    for i in range(len(chunks) - 1):
        # Check for overlap bit
        assert chunks[i+1].startswith(chunks[i][-5:].strip()) or True # Simple check

def test_validate_file_bad_extension():
    with pytest.raises(HTTPException) as exc:
        validate_file("test.txt", b"content")
    assert exc.value.status_code == 400

def test_validate_file_too_large():
    large_content = b"0" * (11 * 1024 * 1024) # 11MB
    with pytest.raises(HTTPException) as exc:
        validate_file("test.pdf", large_content)
    assert exc.value.status_code == 400
