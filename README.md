# ATS Resume Scanner

An AI-powered ATS Resume Scanner and Optimizer built with FastAPI, LangChain, Qdrant, and PostgreSQL.

## Architecture Overview
- **Backend:** FastAPI for high-performance API endpoints.
- **LLM Orchestration:** LangChain for complex prompt chaining and document parsing.
- **Vector Database:** Qdrant for semantic search and resume matching.
- **Primary Database:** PostgreSQL (Supabase) for structured data storage.
- **Task Queue:** Redis & Celery for asynchronous resume processing.
- **File Storage:** Cloudflare R2 for resume and report storage.

## Tech Stack
| Component | Technology |
| --- | --- |
| Framework | FastAPI (Python 3.11+) |
| LLM | GPT-4o / GPT-4o-mini (via OpenRouter) |
| Vector DB | Qdrant |
| Database | PostgreSQL |
| Cache/Queue | Redis |
| Worker | Celery |
| Storage | Cloudflare R2 |

## Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+ (for future frontend)

## Local Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd ats-resume-scanner
   ```

2. **Setup environment variables:**
   ```bash
   cp .env.example .env
   # Fill in the required API keys in .env
   ```

3. **Start infrastructure services:**
   ```bash
   docker-compose -f infra/docker-compose.yml up -d
   ```

4. **Install backend dependencies:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. **Run the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload
   ```

## Verification
Open your browser and navigate to:
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Project Structure
- `backend/`: FastAPI application code.
- `frontend/`: Next.js application (Phase 5).
- `infra/`: Docker and database initialization scripts.
- `shared/`: Constants and utilities shared across the project.

## Development Phases
- **Phase 0:** Project skeleton and infrastructure setup.
- **Phase 1:** Resume ingestion and parsing.
- **Phase 2:** JD analysis and scoring engine.
- **Phase 3:** Enhancement and feedback generation.
- **Phase 4:** Asynchronous processing with Celery.
- **Phase 5:** Frontend development with Next.js.
- **Phase 6:** Deployment and optimization.
