import logging
import json
from typing import Dict, Any, Optional, List
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from app.config import settings

logger = logging.getLogger(__name__)

class PostgresClient:
    _pool: Optional[pool.ThreadedConnectionPool] = None

    def init_pool(self):
        """Initializes the connection pool."""
        try:
            self._pool = pool.ThreadedConnectionPool(
                minconn=2,
                maxconn=10,
                dsn=settings.DATABASE_URL
            )
            logger.info("Database connection pool initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            # Don't raise here, allow health check to report it

    def get_connection(self):
        """Gets a connection from the pool."""
        if not self._pool:
            self.init_pool()
        if self._pool:
            return self._pool.getconn()
        return None

    def release_connection(self, conn):
        """Releases a connection back to the pool."""
        if self._pool and conn:
            self._pool.putconn(conn)

    def check_connection(self) -> bool:
        """Checks if the database connection is working."""
        conn = self.get_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False
        finally:
            self.release_connection(conn)

    def create_resume_job(self, filename: str, user_id: str = None, celery_task_id: str = None) -> str:
        """Inserts a new row into resume_jobs with status='pending'."""
        conn = self.get_connection()
        if not conn:
            raise Exception("Database connection unavailable")
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO resume_jobs (original_filename, user_id, status, celery_task_id) VALUES (%s, %s, 'pending', %s) RETURNING id",
                    (filename, user_id, celery_task_id)
                )
                job_id = cur.fetchone()[0]
                conn.commit()
                return str(job_id)
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to create resume job: {e}")
            raise
        finally:
            self.release_connection(conn)

    def update_resume_job(self, job_id: str, **kwargs) -> None:
        """Updates a resume_jobs row dynamically."""
        if not kwargs:
            return
        
        conn = self.get_connection()
        if not conn:
            raise Exception("Database connection unavailable")
        
        try:
            fields = []
            values = []
            for key, value in kwargs.items():
                fields.append(f"{key} = %s")
                if isinstance(value, (dict, list)):
                    values.append(json.dumps(value))
                else:
                    values.append(value)
            
            values.append(job_id)
            query = f"UPDATE resume_jobs SET {', '.join(fields)}, updated_at = NOW() WHERE id = %s"
            
            with conn.cursor() as cur:
                cur.execute(query, tuple(values))
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to update resume job {job_id}: {e}")
            raise
        finally:
            self.release_connection(conn)

    def get_resume_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Fetches a single resume_jobs row by id."""
        conn = self.get_connection()
        if not conn:
            return None
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM resume_jobs WHERE id = %s", (job_id,))
                return cur.fetchone()
        except Exception as e:
            logger.error(f"Failed to fetch resume job {job_id}: {e}")
            return None
        finally:
            self.release_connection(conn)

    def create_analysis_result(self, resume_job_id: str, jd_job_id: Optional[str],
                               score_total: int, score_breakdown: Dict,
                               gaps: Dict, semantic_similarity: Optional[float] = None,
                               matched_skills: Optional[Dict] = None,
                               enhancements: Optional[List] = None,
                               compliance_issues: Optional[Dict] = None,
                               feedback_text: Optional[str] = None,
                               learning_path: Optional[Dict] = None) -> str:
        """Inserts into analysis_results with all JD-aware metrics and Phase 3 features."""
        conn = self.get_connection()
        if not conn:
            raise Exception("Database connection unavailable")
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO analysis_results 
                       (resume_job_id, jd_job_id, score_total, score_breakdown, gaps, 
                        semantic_similarity, matched_skills, enhancements, 
                        compliance_issues, feedback_text, learning_path) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                    (resume_job_id, jd_job_id, score_total, json.dumps(score_breakdown), 
                     json.dumps(gaps), semantic_similarity, 
                     json.dumps(matched_skills) if matched_skills else None,
                     json.dumps(enhancements) if enhancements else None,
                     json.dumps(compliance_issues) if compliance_issues else None,
                     feedback_text,
                     json.dumps(learning_path) if learning_path else None)
                )
                analysis_id = cur.fetchone()[0]
                conn.commit()
                return str(analysis_id)
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to create analysis result: {e}")
            raise
        finally:
            self.release_connection(conn)

    def get_analysis_result(self, resume_job_id: str) -> Optional[Dict[str, Any]]:
        """Fetch the most recent analysis_result for a given resume_job_id."""
        conn = self.get_connection()
        if not conn:
            return None
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM analysis_results WHERE resume_job_id = %s ORDER BY created_at DESC LIMIT 1",
                    (resume_job_id,)
                )
                return cur.fetchone()
        except Exception as e:
            logger.error(f"Failed to fetch analysis result for {resume_job_id}: {e}")
            return None
        finally:
            self.release_connection(conn)

    def create_jd_job(self, raw_text: str, parsed_data: Dict[str, Any]) -> str:
        """Inserts a new row into jd_jobs."""
        conn = self.get_connection()
        if not conn:
            raise Exception("Database connection unavailable")
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO jd_jobs (raw_text, parsed_data) VALUES (%s, %s) RETURNING id",
                    (raw_text, json.dumps(parsed_data))
                )
                jd_job_id = cur.fetchone()[0]
                conn.commit()
                return str(jd_job_id)
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to create JD job: {e}")
            raise
        finally:
            self.release_connection(conn)

    def get_jd_job(self, jd_job_id: str) -> Optional[Dict[str, Any]]:
        """Fetches a single jd_jobs row by id."""
        conn = self.get_connection()
        if not conn:
            return None
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM jd_jobs WHERE id = %s", (jd_job_id,))
                return cur.fetchone()
        except Exception as e:
            logger.error(f"Failed to fetch JD job {jd_job_id}: {e}")
            return None
        finally:
            self.release_connection(conn)

    def create_ranking_session(self, jd_job_id: str, resume_job_ids: List[str], 
                               ranked_results: List[Dict[str, Any]], user_id: str = None) -> str:
        """Inserts a new row into ranking_sessions."""
        conn = self.get_connection()
        if not conn:
            raise Exception("Database connection unavailable")
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO ranking_sessions 
                       (jd_job_id, resume_job_ids, ranked_results, user_id) 
                       VALUES (%s, %s::uuid[], %s, %s) RETURNING id""",
                    (jd_job_id, resume_job_ids, json.dumps(ranked_results), user_id)
                )
                session_id = cur.fetchone()[0]
                conn.commit()
                return str(session_id)
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to create ranking session: {e}")
            raise
        finally:
            self.release_connection(conn)

    def get_ranking_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Fetches a single ranking session by id."""
        conn = self.get_connection()
        if not conn:
            return None
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM ranking_sessions WHERE id = %s", (session_id,))
                return cur.fetchone()
        except Exception as e:
            logger.error(f"Failed to fetch ranking session {session_id}: {e}")
            return None
        finally:
            self.release_connection(conn)

# Export a single instance
db = PostgresClient()

def init_db_pool():
    db.init_pool()
