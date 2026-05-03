import time
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg2
import redis
import httpx

from app.config import settings
from app.api.routes import resume, jd, score, enhance, rank

logger = logging.getLogger(__name__)

app = FastAPI(
    title="ATS Resume Scanner API",
    description="AI-powered ATS Resume Scanner and Optimizer",
    version="0.1.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.APP_ENV == "development" else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(resume.router)
app.include_router(jd.router)
app.include_router(score.router)
app.include_router(enhance.router)
app.include_router(rank.router)

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "environment": settings.APP_ENV,
        "timestamp": time.time()
    }

from app.db.postgres_client import db, init_db_pool

@app.get("/health/db")
async def db_health():
    if db.check_connection():
        return {"status": "ok", "service": "postgresql"}
    raise HTTPException(status_code=500, detail="Database connection failed")

@app.get("/health/redis")
async def redis_health():
    try:
        # We can eventually move this to redis_client.py
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        return {"status": "ok", "service": "redis"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis connection failed: {str(e)}")

@app.get("/health/qdrant")
async def qdrant_health():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.QDRANT_URL}/healthz")
            if response.status_code == 200:
                return {"status": "ok", "service": "qdrant"}
            else:
                raise Exception(f"Qdrant returned status {response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Qdrant connection failed: {str(e)}")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

from app.db.postgres_client import init_db_pool

@app.on_event("startup")
async def startup_event():
    init_db_pool()
    logger.info("Database pool initialized")

@app.on_event("shutdown")
async def shutdown_event():
    # In Phase 1+, close DB pools/clients here
    pass
