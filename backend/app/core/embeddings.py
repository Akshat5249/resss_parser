import logging
import uuid
import numpy as np
from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams, Distance, PointStruct
)

from app.config import settings
from app.shared.constants import (
    QDRANT_COLLECTION_NAME, EMBEDDING_MODEL, EMBEDDING_DIMENSION
)

logger = logging.getLogger(__name__)

# Initialize Qdrant Client
qdrant_client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None
)

# Initialize Embedder
embedder = OpenAIEmbeddings(
    model=EMBEDDING_MODEL,
    openai_api_key=settings.OPENROUTER_API_KEY,
    openai_api_base=settings.OPENROUTER_BASE_URL,
    dimensions=EMBEDDING_DIMENSION
)

def uuid_to_int(uuid_str: str) -> int:
    """Converts a UUID string to an integer compatible with Qdrant IDs."""
    return int(uuid.UUID(uuid_str).int) % (2**63)

def init_qdrant_collection() -> None:
    """Ensures the Qdrant collection exists."""
    try:
        collections = qdrant_client.get_collections().collections
        exists = any(c.name == QDRANT_COLLECTION_NAME for c in collections)
        
        if not exists:
            qdrant_client.create_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Qdrant collection '{QDRANT_COLLECTION_NAME}' created.")
        else:
            logger.info(f"Qdrant collection '{QDRANT_COLLECTION_NAME}' already exists.")
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant: {e}")
        raise

def embed_text(text: str) -> List[float]:
    """Generates embedding for a single text string."""
    try:
        return embedder.embed_query(text)
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        raise HTTPException(status_code=500, detail="Text embedding generation failed")

def embed_texts(texts: List[str]) -> List[List[float]]:
    """Batch generates embeddings for multiple texts."""
    try:
        return embedder.embed_documents(texts)
    except Exception as e:
        logger.error(f"Batch embedding failed: {e}")
        raise HTTPException(status_code=500, detail="Batch text embedding generation failed")

def store_resume_embedding(job_id: str, text: str, metadata: Dict[str, Any]) -> None:
    """Embeds and stores a resume in Qdrant."""
    vector = embed_text(text)
    point_id = uuid_to_int(job_id)
    
    qdrant_client.upsert(
        collection_name=QDRANT_COLLECTION_NAME,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "job_id": job_id,
                    "type": "resume",
                    **metadata
                }
            )
        ]
    )
    logger.info(f"Stored resume embedding for job {job_id}")

def store_jd_embedding(jd_job_id: str, text: str, metadata: Dict[str, Any]) -> None:
    """Embeds and stores a JD in Qdrant."""
    vector = embed_text(text)
    point_id = uuid_to_int(jd_job_id)
    
    qdrant_client.upsert(
        collection_name=QDRANT_COLLECTION_NAME,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "jd_job_id": jd_job_id,
                    "type": "jd",
                    **metadata
                }
            )
        ]
    )
    logger.info(f"Stored JD embedding for job {jd_job_id}")

def compute_similarity(resume_job_id: str, jd_job_id: str) -> float:
    """Computes cosine similarity between a resume and a JD vector."""
    try:
        resume_point = qdrant_client.retrieve(
            collection_name=QDRANT_COLLECTION_NAME,
            ids=[uuid_to_int(resume_job_id)],
            with_vectors=True
        )
        jd_point = qdrant_client.retrieve(
            collection_name=QDRANT_COLLECTION_NAME,
            ids=[uuid_to_int(jd_job_id)],
            with_vectors=True
        )
        
        if not resume_point or not jd_point:
            logger.warning(f"One or both points not found in Qdrant: resume={resume_job_id}, jd={jd_job_id}")
            return 0.0
            
        v1 = np.array(resume_point[0].vector)
        v2 = np.array(jd_point[0].vector)
        
        similarity = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        return float(similarity)
    except Exception as e:
        logger.error(f"Similarity computation failed: {e}")
        return 0.0

def search_similar_resumes(jd_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Searches for top K resumes similar to the given JD text."""
    vector = embed_text(jd_text)
    
    search_results = qdrant_client.search(
        collection_name=QDRANT_COLLECTION_NAME,
        query_vector=vector,
        query_filter={
            "must": [
                {"key": "type", "match": {"value": "resume"}}
            ]
        },
        limit=top_k
    )
    
    return [
        {
            "job_id": hit.payload["job_id"],
            "score": hit.score,
            "metadata": hit.payload
        }
        for hit in search_results
    ]
