import time
import logging
import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.routes import resume, jd, score, enhance, rank, analyze, report
from app.db.postgres_client import db, init_db_pool
from app.db.redis_client import redis_client, init_redis
from app.core.embeddings import init_qdrant_collection

logger = logging.getLogger(__name__)

app = FastAPI(
    title="ATS Resume Scanner API",
    description="AI-powered ATS Resume Scanner and Optimizer",
    version="0.1.0"
)

# CORS Middleware
allowed_origins = (
    ["*"] if settings.APP_ENV == "development"
    else [
        "https://ats-scanner-XXXX.vercel.app", # Placeholder - update after Vercel deployment
        "http://localhost:3000",
        os.getenv("FRONTEND_URL", ""),
    ]
)
# Remove empty strings
allowed_origins = [o for o in allowed_origins if o]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
app.include_router(analyze.router)
app.include_router(report.router)


@app.get("/health")
async def health_check():
    db_status = "ok" if db.check_connection() else "error"
    redis_status = "ok" if redis_client.check_connection() else "error"
    
    qdrant_status = "error"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.QDRANT_URL}/healthz")
            if resp.status_code == 200:
                qdrant_status = "ok"
    except:
        pass

    return {
        "status": "ok" if all(s == "ok" for s in [db_status, redis_status, qdrant_status]) else "degraded",
        "environment": settings.APP_ENV,
        "timestamp": time.time(),
        "services": {
            "database": db_status,
            "redis": redis_status,
            "qdrant": qdrant_status
        }
    }

@app.get("/health/db")
async def db_health():
    if db.check_connection():
        return {"status": "ok", "service": "postgresql"}
    raise HTTPException(status_code=500, detail="Database connection failed")

@app.get("/health/redis")
async def redis_health():
    if redis_client.check_connection():
        return {"status": "ok", "service": "redis"}
    raise HTTPException(status_code=500, detail="Redis connection failed")

@app.get("/health/qdrant")
async def qdrant_health():
    try:
        qdrant_client.get_collections()
        return {"status": "ok", "service": "qdrant"}
    except Exception as e:
        logger.error(f"Detailed Qdrant health failure: {e}")
        raise HTTPException(status_code=500, detail=f"Qdrant connection failed: {str(e)}")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.on_event("startup")
async def startup_event():
    init_db_pool()
    init_redis()
    try:
        init_qdrant_collection()
        logger.info("Qdrant collection initialized")
    except Exception as e:
        logger.warning(f"Qdrant init failed: {e}")
    logger.info("Application startup: DB, Redis, and Qdrant initialized")

@app.on_event("shutdown")
async def shutdown_event():
    pass
