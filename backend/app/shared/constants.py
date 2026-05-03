from enum import Enum

SCORE_WEIGHTS = {
    "skill_match": 0.40,
    "experience": 0.25,
    "projects": 0.15,
    "education": 0.10,
    "formatting": 0.10
}

SUPPORTED_FILE_TYPES = [".pdf", ".docx"]
MAX_FILE_SIZE_MB = 10

QDRANT_COLLECTION_NAME = "resume_embeddings"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536  # for text-embedding-3-small

PARSER_LLM_MODEL = "openai/gpt-4o-mini"     # cheap, fast — for extraction
ENHANCEMENT_LLM_MODEL = "openai/gpt-4o"     # quality — for rewriting

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"
